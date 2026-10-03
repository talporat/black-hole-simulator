#pragma once
#include "gl/gl.h"

// Off-screen render target with a single colour texture.
class Framebuffer {
public:
    // (Re)allocates only when the size or format changes.
    void ensure(int width, int height, GLenum internalFormat);
    void bind() const;
    void bindTexture(int unit) const;
    int width() const { return width_; }
    int height() const { return height_; }

private:
    GLuint fbo_ = 0, tex_ = 0;
    int width_ = 0, height_ = 0;
    GLenum format_ = 0;
};
