# Rendering Videos on the EU4 Time Line

![image](bad_apple.PNG)

This repository contains code to create an eu4-savefile that plays back a video in question. Currently only supports Black-And-White Videos.

**==> Try out the [Demo](https://colab.research.google.com/drive/12X675Pgz7vay6fsIFJaFiYsINhr4xiZc?usp=sharing)!**

**Currently only supports a folder of frames. If you have a video, you need to convert it to frames first, e.g.using ffmpeg.**

Make sure, requirements.txt is satisfied. 

The code executed with the command line:

    python main.py 
        -i <frame_dir> 
        -f1 <first_frame> 
        -o <output_file> 
        -eu4 <base_save_file> 
        --mod_dir <eu4_game_file_dir> 
        -d <definition> 
        -p <province_map> 
        
        --crop <crop_values> 
        --resize <resize_shape>
    
        --colouring <colouring_mode>
        --ncolours <number of colours for quantization>

Use the following command to get additional info on the arguments and a list of all available arguments:

`python main.py -h`

----

**frame_dir**: Path to your folder of frames

**first_frame**: name of the first frame (e.g. frame1.jpg). The next frames will be inferred by incrementing the number at the end.

**output_file**: Name and location of the new eu4-savefile. Has to end with ".eu4" (e.g. "./xd.eu4")

**base_save_file**: Provide the path to an eu4-savefile, that is the basis for any modification. A new savefile is recommended

-----
**Either:**

**eu4_game_files_dir**: provide a path to where eu4 is saved, if you are using the base map, otherwise provide a path to the mod.

**Or:**

**province_map**: usually called "provinces.bmp", found under `<PATHTOEU4>/map`. Maps pixel-location to a colour.

**definition**: usually called "definition.csv", found under `<PATHTOEU4>/map`. Maps Colour to Province.

If province_map and definition are provided, they are prioritized. But you have to provide either both or the PATHTOEU4. 

----- 
**crop_values**: LEFT UPPER RIGHT LOWER (e.g. 0 0 60 60); crops the bmp at these bounds in the image. You might need to open the image with sth like GIMP to find good crop values. This way you can specify where on the worldmap the video renders (You can also just crop it yourself and pass the generated new bmp as an argument. Refer to province_map)

**resize_shape**: W H (e.g. 75 100); New height and width values; Rescales of the province map before computation. This speeds up computation, but comes at the cost of more artifacts.

---

**colouring**: choose from (bw, gray, simple, infer)

bw and gray for black/white and grayscale images respectively

simple: creates a few (256 or less) colours from the entire colour space and quantizes colours in the video to these values; Quantization currently needed due to colour number being tied to the number of tags.

infer: infers palette (256 colours or less) from the first frame of the video. Very good if it is a good predictor for the rest of the frames;
    
    usecases include single images, short gifs, animations with flat shading etc.
    
**ncolours**: number of colours for quantization, can be any number between 2-256 

