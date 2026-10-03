#include "png.h"

#include <cstdio>
#include <cstring>
#include <vector>

namespace {

uint32_t crc32(const uint8_t* data, size_t n, uint32_t crc = 0) {
    static uint32_t table[256];
    if (!table[1]) {
        for (uint32_t i = 0; i < 256; ++i) {
            uint32_t c = i;
            for (int k = 0; k < 8; ++k) c = (c & 1) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
            table[i] = c;
        }
    }
    crc = ~crc;
    for (size_t i = 0; i < n; ++i) crc = table[(crc ^ data[i]) & 0xFF] ^ (crc >> 8);
    return ~crc;
}

void put32(std::vector<uint8_t>& v, uint32_t x) {
    for (int s = 24; s >= 0; s -= 8) v.push_back(uint8_t(x >> s));
}

void writeChunk(std::FILE* f, const char* type, const std::vector<uint8_t>& data) {
    std::vector<uint8_t> buf;
    put32(buf, uint32_t(data.size()));
    buf.insert(buf.end(), type, type + 4);
    buf.insert(buf.end(), data.begin(), data.end());
    put32(buf, crc32(buf.data() + 4, buf.size() - 4));
    std::fwrite(buf.data(), 1, buf.size(), f);
}

}  // namespace

bool writePng(const char* path, int width, int height, const uint8_t* rgb) {
    std::FILE* f = std::fopen(path, "wb");
    if (!f) return false;

    // Scanlines, each prefixed with filter type 0 (none).
    size_t stride = size_t(width) * 3;
    std::vector<uint8_t> raw((stride + 1) * height);
    for (int y = 0; y < height; ++y) {
        raw[y * (stride + 1)] = 0;
        std::memcpy(&raw[y * (stride + 1) + 1], rgb + y * stride, stride);
    }

    // zlib stream made of uncompressed deflate blocks (max 65535 bytes each).
    std::vector<uint8_t> z = {0x78, 0x01};
    uint32_t a = 1, b = 0;  // adler32
    for (size_t pos = 0; pos < raw.size();) {
        size_t n = raw.size() - pos < 65535 ? raw.size() - pos : 65535;
        z.push_back(pos + n == raw.size() ? 1 : 0);
        z.push_back(uint8_t(n));
        z.push_back(uint8_t(n >> 8));
        z.push_back(uint8_t(~n));
        z.push_back(uint8_t(~n >> 8));
        for (size_t i = 0; i < n; ++i) {
            a = (a + raw[pos + i]) % 65521;
            b = (b + a) % 65521;
        }
        z.insert(z.end(), raw.begin() + pos, raw.begin() + pos + n);
        pos += n;
    }
    put32(z, (b << 16) | a);

    const uint8_t sig[8] = {0x89, 'P', 'N', 'G', '\r', '\n', 0x1A, '\n'};
    std::fwrite(sig, 1, 8, f);
    std::vector<uint8_t> ihdr;
    put32(ihdr, uint32_t(width));
    put32(ihdr, uint32_t(height));
    ihdr.insert(ihdr.end(), {8, 2, 0, 0, 0});  // 8-bit, RGB
    writeChunk(f, "IHDR", ihdr);
    writeChunk(f, "IDAT", z);
    writeChunk(f, "IEND", {});
    return std::fclose(f) == 0;
}
