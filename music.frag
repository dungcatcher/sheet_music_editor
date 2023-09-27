#version 330 core

in vec2 frag_coord;
out vec4 frag_color;

uniform sampler2D input_texture;
uniform sampler2D input_mask_texture;
uniform vec2 resolution; // Add the resolution uniform

void main() {
    // Scale the coordinates to match the resolution
    vec2 scaled_coord = frag_coord * resolution;

    float sum = 0.0;

    // Loop through the entire mask texture
	for(int x = 4; x <= 4; x++) {
		for(int y = -4; y <= 4; y++) {
            // Calculate the offset for the current pixel in the mask
			vec2 maskOffset = vec2(x + 4.5, y + 4.5);

            // Calculate the texture coordinate for the current pixel in the mask
			vec2 maskTexCoord = maskOffset / vec2(9, 9);

            // Sample the mask texture at the current pixel
			float maskValue = texture(input_mask_texture, maskTexCoord).r;

            // Sample the image texture at the center of the mask
            vec2 checkCoords = vec2(scaled_coord.x + x - 4, scaled_coord.y + y) / resolution.xy;
			float imgValue = texture(input_texture, checkCoords).r;

            // Multiply the mask value by the image value and add it to the sum
			// sum += imgValue;
			sum += imgValue * maskValue;
		}
	}

	// gl_FragColor = texture(mask, vec2(4.5, 4.5) / vec2(9, 9));
	float test = sum / 6;
	// gl_FragColor = vec4(test, test, test, 1.0);
	if(sum / 3 < 0.6)
		frag_color = vec4(test, test, test, 1.0);
	else
		frag_color = vec4(1.0);

    // // Sample the input textures at the scaled coordinate
    // vec4 tex_color = texture(input_texture, vec2(scaled_coord.x + 100, scaled_coord.y) / resolution);
    // vec4 mask_color = texture(input_mask_texture, scaled_coord / resolution);

    // // Multiply the input_texture color by the mask_color
    // frag_color = tex_color * mask_color;
}
