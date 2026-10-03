cmake_minimum_required(VERSION 3.20)
project(BlackHole LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# GLFW (window + GL context) is the only external dependency.
include(FetchContent)
set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(GLFW_INSTALL OFF CACHE BOOL "" FORCE)
FetchContent_Declare(glfw
  GIT_REPOSITORY https://github.com/glfw/glfw.git
  GIT_TAG 3.4
  GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(glfw)

find_package(OpenGL REQUIRED)

add_executable(blackhole
  src/main.cpp
  src/camera.cpp
  src/png.cpp
  src/gl/shader.cpp
  src/gl/framebuffer.cpp)
target_include_directories(blackhole PRIVATE src)
target_compile_definitions(blackhole PRIVATE SHADER_DIR="${CMAKE_SOURCE_DIR}/shaders")
target_link_libraries(blackhole PRIVATE glfw OpenGL::GL)

# CPU tests of the same GLSL geodesic code the shader runs.
enable_testing()
add_executable(test_geodesic tests/test_geodesic.cpp src/camera.cpp)
target_include_directories(test_geodesic PRIVATE src)
add_test(NAME geodesic COMMAND test_geodesic)

# The step-by-step programs built in the video series.
foreach(stage 01_rays_2d 02_raytracer_3d 03_disk)
  if(EXISTS ${CMAKE_SOURCE_DIR}/stages/${stage}/main.cpp)
    string(SUBSTRING ${stage} 0 2 number)
    add_executable(stage${number} stages/${stage}/main.cpp)
    target_compile_definitions(stage${number} PRIVATE
      STAGE_DIR="${CMAKE_SOURCE_DIR}/stages/${stage}")
    target_link_libraries(stage${number} PRIVATE glfw OpenGL::GL)
  endif()
endforeach()
