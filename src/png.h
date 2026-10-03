#pragma once
#include <cstdint>

// Writes an 8-bit RGB PNG. Pixels are top row first, 3 bytes per pixel.
// The image data is stored uncompressed (deflate "stored" blocks).
bool writePng(const char* path, int width, int height, const uint8_t* rgb);
