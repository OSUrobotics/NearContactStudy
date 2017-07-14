function GradientColorBoard(width,height)

    pixels_cm = 381;
    
    width_pixels = floor(width * pixels_cm);
    height_pixels = floor(height * pixels_cm);
    
    color1_initial = [0,0,0];
    color2_initial = [1,1,1];
    
    checkerboard = ones(width_pixels, height_pixels, 3);
    
    w_colorstep = 1/width_pixels;
    h_colorstep = 1/height_pixels;
    for iw = 1:width_pixels
        w_color = iw * w_colorstep;
        for ih = 1:height_pixels
            h_color = ih * h_colorstep;
            checkerboard(iw, ih, :) = [1, w_color, h_color];
        end
    end
    image(checkerboard)
    imwrite(checkerboard, 'GradientColorboard.png')
end