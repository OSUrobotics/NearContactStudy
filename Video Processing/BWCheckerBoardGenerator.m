function BWCheckerBoardGenerator(square_length, width, height)
    % Checkboard that is made up of two colors
    % square_length = cms
    % width = paper width in cms
    % height = paper height in cms
    % large squares: BWCheckerBoardGenerator(6, 20, 25)
    % medium squares: BWCheckerBoardGenerator(2*sqrt(3), 20, 25)
    % small squares: BWCheckerBoardGenerator(2, 20, 25)
    
    pixels_cm = 244;
    
    % black and white
%     color1_initial = [0.0, 0.0, 0.0];
%     color2_initial = [1.0, 1.0, 1.0];
    
    % grey and dark grey
%     color1_initial = [0.169, 0.169, 0.169];
%     color2_initial = [0.79, 0.79, 0.79];

    % blue and yellow
    color1_initial = [0.0, 0.0, 1.0];
    color2_initial = [1.0, 1.0, 0.0];
    
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
        color1(3) = color1_initial(3); % make the gradation step smarter
        % unique colors for every square instead of varying horizontaly and
        % vertically independently
        for i_h = 1:length(h_start)
            color2 = color2_initial;
            color2(1) = color2_initial(1);
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
    imwrite(checkerboard, 'BWCheckerboard.png')
end