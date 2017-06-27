% % % Generate Shapes for Study

base_dir = 'Shapes';
shapes = {'cube', 'ellipse', 'cylinder','cone', 'handle'};
resolution = [10, 100, 50,50,100]; %certain resolutions do not produce an image
% dimensions in cm
width  = 3:3:9;
widthr = 0.3:0.3:0.9; % for handle only
height = 3:3:9;
extent = 3:3:9;
extentr = 0.3:0.3:0.9; % for handle only
r = (1:1:3)/10; % radius of handle
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
                if strcmpi(shapes{is}, 'handle')
                    for ir = 1:size(r, 2)
                        filename = sprintf('%s/%s_h%d_w%d_e%d_a%d', base_dir, shapes{is}, height(ih), widthr(iw), extentr(ie),r(ir));
                        ShapeSTLGenerator(shapes(is), resolution(is), filename, height(ih)/100, widthr(iw)/100, extentr(ie)/100, r(ir)/100)
                    end
                end
                else
                    filename = sprintf('%s/%s_h%d_w%d_e%d', base_dir, shapes{is}, height(ih), width(iw), extent(ie));
                    ShapeSTLGenerator(shapes(is), resolution(is), filename, height(ih)/100, width(iw)/100, extent(ie)/100)
                end
            end
        end
    end
end



% width  = 3:3:9;
% height = 3:3:9;
% extent = 3:3:9;
% is = 5; %1:size(shapes,2)
% for ih = 1:size(height,2)
%     for iw = 1:size(width,2)
%         for ie = 1:size(extent,2)
%             if strcmpi(shapes{is}, 'cone')
%                 for ia = 1:size(alpha,2)
%                     filename = sprintf('%s/%s_h%d_w%d_e%d_a%d', base_dir, shapes{is}, height(ih), width(iw), extent(ie),alpha(ia));
%                     ShapeSTLGenerator(shapes(is), resolution(is), filename, height(ih)/100, width(iw)/100, extent(ie)/100, alpha(ia))
%                 end
%             if strcmpi(shapes{is}, 'handle')
%                 for ir = 1:size(r, 2)
%                     filename = sprintf('%s/%s_h%d_w%d_e%d_a%d', base_dir, shapes{is}, height(ih), width(iw), extent(ie),r(ir));
%                     ShapeSTLGenerator(shapes(is), resolution(is), filename, height(ih)/100, width(iw)/100, extent(ie)/100, r(ir)/100)
%                 end
%             end
%             else
%                 filename = sprintf('%s/%s_h%d_w%d_e%d', base_dir, shapes{is}, height(ih), width(iw), extent(ie));
%                 ShapeSTLGenerator(shapes(is), resolution(is), filename, height(ih)/100, width(iw)/100, extent(ie)/100)
%             end
%         end
%     end
% end