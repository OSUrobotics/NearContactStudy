function assembleGrid(square_length, width, height)
% Create a grid from black squares and white squares with circles in them
% square_length is the length in cms of each edge of the squares in the grid
% height and width are dimensions in cm for total grid size -- this should
% match the object or table that it will be covering

% Cylinder: 2.5, 6.5 * pi, 15.5


pixels_cm = 381;


% create white squares with unique circles
square_pixels = floor(square_length * pixels_cm);
% CheckerCodeGenerator(square_pixels)

% create a black square (black is [0,0,0])
black_square = zeros(square_pixels, square_pixels, 3);



% get pixel size of image
width_pixel = floor(width * pixels_cm);
height_pixel = floor(height * pixels_cm);

% create empty image
Image = ones(width_pixel, height_pixel, 3);

col_start = 1:square_pixels:(width_pixel-square_pixels);
col_end = col_start + square_pixels - 1;
row_start = 1:square_pixels:(height_pixel-square_pixels);
row_end = row_start + square_pixels - 1;
%

image_count = 1;

for i_c = 1:length(col_start)
    for i_r = 1:length(row_start)
        y_idx = row_start(i_r):row_end(i_r);
        x_idx = col_start(i_c):col_end(i_c);
        if mod(i_c + i_r,2) == 0
            Image(x_idx, y_idx, :) = black_square;
        else
            color_square_fn = char(strcat('images/color', string(image_count), '.png')); %i don't think this will work on Windows
            color_square = imread(color_square_fn);
            Image(x_idx, y_idx, :) = color_square;
            image_count = image_count + 1;
        end
%         image(Image)
            
    end
end
image(Image)
imwrite(Image, 'CylinderColoredCheckerboard.png')

end