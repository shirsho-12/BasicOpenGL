"""

"""

import classes
import os

# vertex shader string
strVS = """
#version 330 core

layout(location = 0) in vec3 aVert;
uniform mat4 uMVMatrix;
uniform mat4 uPMatrix;
uniform float uTheta;

out vec2 vTexCoord;

void main(){
    // rotational transform
    mat4 rot = mat4(vec4(cos(uTheta), sin(uTheta), 0.0, 0.0),
                    vec4(-sin(uTheta), cos(uTheta), 0.0, 0.0),
                    vec4(0.0, 0.0, 1.0, 0.0),
                    vec4(0.0, 0.0, 0.0, 1.0)
                    );
    // transform vertex
    gl_Position = uPMatrix * uMVMatrix * rot * vec4(aVert, 1.0);
    // set texture coordinate
    vTexCoord = aVert.xy + vec2(0.5, 0.5);
}
"""

# Fragment Shader string
strFS= """

#version 330 core
#define M_PI 3.1415926535897932384626433832795

in vec4 vCol;
in vec2 vTexCoord;

uniform sampler2D tex2D;
uniform bool showCircle;

out vec4 fragColor;

void main(){
    if (showCircle){
    // discard fragment outside circle
        float r = distance(vTexCoord, vec2(0.5, 0.5));
        if (sin(16*M_PI*r) < 0.0) {
            discard;
        }
        else {
            fragColor = texture(tex2D, vTexCoord);
        }
    }
        else{
            fragColor = texture(tex2D, vTexCoord);
    }
}
"""


if __name__ == '__main__':
    print("Starting simple GLFW. Press any key to toggle. \nPress ESC to quit.")
    rw = classes.RenderWindow(strVS, strFS)
    rw.run()
