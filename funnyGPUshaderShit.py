from PIL import Image
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np
import moderngl
import numpy as np
from PIL import Image

def remove_stave(data_range, image, x_thresh, y_thresh, recursions=2):

    # The most crap way of doing it
    # Is there a way of running this only on the bar line and maybe the 2 lines above and below

    image_copy = image.copy()

    x1, y1 = data_range[0]
    x2, y2 = data_range[1]

    cropped_image = image_copy.crop((x1 - 4, y1 - 4, x2 + 4, y2 + 4))

    cropped_image.save('input.png')
    mask_image_path = 'mask.png'
    fragment_shader_path = 'music.frag'
    output_image = apply_shader(cropped_image, mask_image_path, fragment_shader_path)
    output_image.save("test_output.png")
    width, height = output_image.size
    output_image = output_image.crop((4, 4, width - 4, height - 4))

    image_copy.paste(output_image, (x1, y1), output_image)

    return image_copy


def apply_shader(input_image, mask_image_path, fragment_shader_path):
    # Load the input image and mask image
    mask_image = Image.open(mask_image_path)

    # Create a ModernGL context
    ctx = moderngl.create_standalone_context()

    # Create a framebuffer to render the image
    width, height = input_image.size
    framebuffer = ctx.framebuffer(color_attachments=[ctx.texture((width, height), 4)])

    # Load and compile the fragment shader
    with open(fragment_shader_path, 'r') as shader_file:
        fragment_shader_source = shader_file.read()
    program = ctx.program(
        vertex_shader="""
            #version 330
            in vec2 in_vert;
            out vec2 frag_coord;
            void main() {
                frag_coord = in_vert * 0.5 + 0.5;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
        """,
        fragment_shader=fragment_shader_source,
    )

    # Create a vertex buffer with the coordinates of a fullscreen quad
    vertices = np.array([-1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0], dtype='f4')
    vbo = ctx.buffer(vertices)
    vao = ctx.simple_vertex_array(program, vbo, 'in_vert')

    # Bind the framebuffer
    framebuffer.use()

    # Render the input image with the shader
    program['input_texture'].value = 0
    program['input_mask_texture'].value = 1
    program['resolution'].value = (width, height)  # Pass resolution as a vec2

    if input_image.mode != 'RGBA':
        input_image = input_image.convert('RGBA')

    input_texture = ctx.texture(input_image.size, 4, input_image.tobytes())
    input_texture.use(location=0)

    mask_texture = ctx.texture(mask_image.size, 4, mask_image.tobytes())
    mask_texture.use(location=1)

    vao.render(moderngl.TRIANGLE_STRIP)

    # Read the rendered image from the framebuffer
    output_image = Image.frombytes('RGBA', framebuffer.size, framebuffer.read(components=4))

    # Cleanup
    framebuffer.release()
    input_texture.release()
    mask_texture.release()

    return output_image
