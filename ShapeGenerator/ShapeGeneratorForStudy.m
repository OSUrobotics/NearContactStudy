% % % Generate Shapes for Study
base_dir = 'Shapes'
% base_dir = '/Volumes/UBUNTU 14_0/Shapes';
shapes = {'cube', 'ellipse', 'cylinder', 'cone', 'vase' };
resolution = [10, 100, 25, 25, 25]; %certain resolutions do not produce an image
% dimensions in cm
% width  = [1,3:3:12];
width  = [1,3:3:12,18];
height = [1,3:3:12,18,24,30];
extent = [1,3:3:12,18,24,30];
alpha = 10:10:30; % degrees
min_d = width/2;
for is = 5 %1:size(shapes,2)
% for is = 1:size(shapes, 2)
    for ih = 1:size(height,2)
        for iw = 1:size(width,2)
            for ie = 1:size(extent,2)
                if strcmpi(shapes{is}, 'cone')
                    for ia = 1:size(alpha,2)
                        filename = sprintf('%s/%s_h%d_w%d_e%d_a%d', base_dir, shapes{is}, height(ih), width(iw), extent(ie),alpha(ia));
                        ShapeSTLGenerator(shapes(is), resolution(is), filename, height(ih)/100, width(iw)/100, extent(ie)/100, alpha(ia))
                    end
                elseif strcmpi(shapes{is}, 'vase')
                    for id = 1:size(min_d, 2)
                        filename = MakeShapeFileName('%s/%s_h%d_w%d_e%d_a%d', {base_dir, shapes{is}, height(ih), width(iw), extent(ie),min_d(id)});
                        ShapeSTLGenerator(shapes(is), resolution(is), filename, height(ih)/100, width(iw)/100, extent(ie)/100, min_d(id)/100)
                    end
                else
                    filename = sprintf('%s/%s_h%d_w%d_e%d', base_dir, shapes{is}, height(ih), width(iw), extent(ie));
                    ShapeSTLGenerator(shapes(is), resolution(is), filename, height(ih)/100, width(iw)/100, extent(ie)/100)
                end
            end
        end
    end
end

%%
shapes = {'handle'};
widthr = width/2; % for handle only
heightr = height * 3;
extentr = extent/10; % for handle only
r = ([1,3:3:12])/2; % radius of handle
for is = 1
    if strcmpi(shapes{is}, 'handle')
        for ih = 1:size(heightr, 2)
            for iw = 1:size(width, 2)
                for ie = 1:size(extent,2)
                     for ir = 1:size(r, 2)
                         % save filename is different because of decimal
                         % places
                         filename = sprintf('%s/%s_h%d_w%0.1f_e%0.1f_a%0.1f', base_dir, shapes{is}, heightr(ih), width(iw), extentr(ie), r(ir));
                         filename = strrep(filename, '.','');
                         try
                             ShapeSTLGenerator(shapes(is), resolution(is), filename, heightr(ih)/100, width(iw)/100, extentr(ie)/100, r(ir)/100)
                         catch
                             disp(filename) %just keep going with loop
                         end
                     end
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