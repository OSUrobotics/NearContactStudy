% % % Generate Shapes for Study

base_dir = 'Shapes';
shapes = {'cube', 'ellipse', 'cylinder','cone'};
resolution = [10, 100, 50,50]; %certain resolutions do not produce an image
% dimensions in cm
width  = 3:3:9;
height = 3:3:9;
extent = 3:3:9;
alpha = 30:15:60; % degrees
for is = 4 %1:size(shapes,2)
    for ih = 1:size(height,2)
        for iw = 1:size(width,2)
            for ie = 1:size(extent,2)
                if strcmpi(shapes{is}, 'cone')
                    for ia = 1:size(alpha,2)
                        filename = sprintf('%s/%s_h%d_w%d_e%d_a%d', base_dir, shapes{is}, height(ih), width(iw), extent(ie),alpha(ia));
                        ShapeSTLGenerator(shapes(is), resolution(is), filename, height(ih)/100, width(iw)/100, extent(ie)/100, alpha(ia))
                    end
                else
                    filename = sprintf('%s/%s_h%d_w%d_e%d', base_dir, shapes{is}, height(ih), width(iw), extent(ie));
                    ShapeSTLGenerator(shapes(is), resolution(is), filename, height(ih)/100, width(iw)/100, extent(ie)/100)
                end
            end
        end
    end
end