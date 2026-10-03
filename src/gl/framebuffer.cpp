#include "gl/framebuffer.h"

#include <cstdio>

void Framebuffer::ensure(int width, int height, GLenum internalFormat) {
    if (width < 1) width = 1;
    if (height < 1) height = 1;
    if (fbo_ && width == width_ && height == height_ && internalFormat == format_) return;
    if (!fbo_) {
        glGenFramebuffers(1, &fbo_);
        glGenTextures(1, &tex_);
    }
    width_ = width;
    height_ = height;
    format_ = internalFormat;

    glBindTexture(GL_TEXTURE_2D, tex_);
    bool hdr = internalFormat == GL_RGBA16F;
    glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, width, height, 0, GL_RGBA,
                 hdr ? GL_FLOAT : GL_UNSIGNED_BYTE, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

    glBindFramebuffer(GL_FRAMEBUFFER, fbo_);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex_, 0);
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
        std::fprintf(stderr, "framebuffer: incomplete (%dx%d)\n", width, height);
}

void Framebuffer::bind() const {
    glBindFramebuffer(GL_FRAMEBUFFER, fbo_);
    glViewport(0, 0, width_, height_);
}

void Framebuffer::bindTexture(int unit) const {
    glActiveTexture(GL_TEXTURE0 + unit);
    glBindTexture(GL_TEXTURE_2D, tex_);
}
