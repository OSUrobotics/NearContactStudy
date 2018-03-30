function ColoredCheckerBoardGenerator(square_length, width, height)
    % Checkboard that is made up of two colors

    pixels_cm = 381;
    
    color1_initial = [0.2, 0.2, 0.0];
    color2_initial = [1.0, 0.8, 0.8];
    
    width_pixels = floor(width * pixels_cm);
    height_pixels = floor(height * pixels_cm);
    square_pixels = floor(square_length * pixels_cm);
    
    
    w_end = square_pixels:square_pixels:width_pixels;
    h_end = square_pixels:square_pixels:height_pixels;
    %w_end = square_pixels:square_pixels+10:width_pixels;
    %h_end = square_pixels:square_pixels+10:height_pixels;
    w_start = w_end - square_pixels + 1;
    h_start = h_end - square_pixels + 1;
    
    checkerboard = ones(width_pixels, height_pixels, 3);
    % insert some vertical spacing lines between certain checkerboard
    % segments?
    for i_w = 1:length(w_start)
        color1 = color1_initial;
        color1(3) = color1_initial(3) + i_w/10; % make the gradation step smarter
        % unique colors for every square instead of varying horizontaly and
        % vertically independently
        for i_h = 1:length(h_start)
            color2 = color2_initial;
            color2(1) = color2_initial(1) - i_h/10;
            if mod(i_w + i_h, 2) == 0
                square_color = color1;
            else
                square_color = color2;
            end
            for pixel_w = w_start(i_w):w_end(i_w)
                for pixel_h = h_start(i_h):h_end(i_h)
                    checkerboard(pixel_w, pixel_h, :) = square_color;
                end
            end
        end
    end
    
    image(checkerboard)
    imwrite(checkerboard, 'ColoredCheckerboard.png')
end