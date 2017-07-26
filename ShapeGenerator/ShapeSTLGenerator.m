function ShapeSTLGenerator(shape_type, resolution, filename, height, width, extent, alpha)
%Description: Create shapes for near contact study and output STL files
%Author: Ammar Kothari - 5/21/17
%Inputs: string for defining shape type, features of shape (height, width,
%extent), and number of points in shell (resolution), filename to save stl
%outputs: none, but a file is created
    if nargin < 6
        disp('Not Enough Inputs');
    elseif nargin == 6
        alpha = NaN;
    end
        
    filename = check_filename(filename);
    if strcmpi(shape_type,'cube')
        Cube(height, width, extent, resolution, filename);
    elseif strcmpi(shape_type,'ellipse')
        Ellipse(height, width, extent, resolution, filename);
    elseif strcmpi(shape_type, 'cylinder')
        Cylinder(height, width, extent, resolution, filename);
    elseif strcmpi(shape_type, 'cone') && ~isnan(alpha)
        Cone(height, width, extent, alpha, resolution, filename);
        disp('Creating Cone');
    elseif  strcmpi(shape_type, 'cone') && isnan(alpha)
        disp('Need alpha to create cone');
    elseif strcmpi(shape_type, 'handle') && ~isnan(alpha)
    	Handle(height, width, extent, alpha, resolution, filename)
        disp('Creating Handle')
    elseif  strcmpi(shape_type, 'handle') && isnan(alpha)
        disp('Need alpha to create handle');
    elseif  strcmpi(shape_type, 'vase') && ~isnan(alpha)
        Vase(height, width, extent, alpha, resolution, filename);
        disp('Creating Vase');
    elseif  strcmpi(shape_type, 'vase') && isnan(alpha)
        disp('Need alpha to create vase');
    elseif  strcmpi(shape_type, 'cone') && isnan(alpha)
        disp('Need alpha to create cone');
    else
        disp('Invalid shape type')
    end

end

function [fname] = check_filename(filename)
%Description: check filename to ensure it has .stl, add if it doens't
%Author: Ammar Kothari 5/21/17
%Inputs: original filename
%Output: filename with .stl as a string
    if ~contains(filename,'.stl')
        fname = strcat(filename,'.stl');
    else
        fname = filename;
    end
end

function Cube(height, width, extent, resolution, filename)
%Description: Create cube STL object
%Author: Ammar Kothari 5/21/17
%Inputs: features of cube and number of points on each surface, filename
%to save file to
%Output: none
%saves STL to file
  
    V_val = 0.9;
    X_span = linspace(-width/2,width/2,resolution);
    Y_span = linspace(-height/2,height/2,resolution);
    Z_span = linspace(-extent/2,extent/2,resolution);
    V = V_val * ones(length(X_span), length(X_span), length(Y_span))/10;
    V(1,:,:) = V_val; V(end,:,:) = V_val;
    V(:,1,:) = V_val; V(:,end,:) = V_val;
    V(:,:,1) = V_val; V(:,:,end) = V_val;
    fv = isosurface(X_span, Y_span, Z_span, V);
    stlwrite(filename, fv, 'mode', 'ascii')
end

function Ellipse(height, width, extent, resolution, filename)
    xc = 0;
    yc = 0;
    zc = 0;
    xr = width;
    yr = height/2;
    zr = extent/2;
    n = resolution;
    [x,y,z] = ellipsoid(xc,yc,zc,xr,yr,zr,n);
    fvc = surf2patch(x,y,z,'triangles');
    stlwrite(filename, fvc, 'mode', 'ascii')
end

function Cylinder(height, width, extent, resolution, filename)
    [X, Z, Y] = cylinder(1, resolution);
    %Scale
    X = X * (width/2);
    Y = (Y - 0.5) * (height); % move centroid to origin
    Z = Z * (extent/2);
    %add bottom and top
    [x_end, y_end, z_end] = ellipsoid(0,0,0,width/2, 0, extent/2, resolution);
    y_top = y_end + height/2;
    y_bot = y_end - height/2;
    x_surf = [x_end;X;x_end];
    z_surf = [z_end;Z;z_end];
    y_surf = [y_bot;Y;y_top];
    fvc = surf2patch(x_surf,y_surf,z_surf,'triangles');
    stlwrite(filename, fvc, 'mode', 'ascii')

end

function Cone(height, width, extent, alpha, resolution, filename)
%something weird here wtih top, bottom, and -1 multiplaction at end
    % unit cone with specified alpha
    % top and bottom are switched (based on matlab command) so orients
    % upward in openrave.  Could fix it there, but seemed easier here
    r_top = 0.5;
    r_bottom = 0.5 - sind(alpha);
    % check that alpha is between 0 and 90
    if ~((0 <= alpha) && (alpha <= 90))
        disp('STL Not Created: Angle Not in Range')
        return
    end
    % check to make sure it doesn't become an hour glass
%     r_test_top = min(width, extent);
%     r_test_bottom = r_test_top - sind(alpha)
    if ((r_top - r_bottom) * tand(alpha) >= 1) || r_bottom < 0
        disp('STL Not Created: Not a Cone')
        return
    end 
    [X, Y, Z] = cylinder([r_top, r_bottom], resolution);
    %add top and bottom;
    [x_top, y_top, z_top] = ellipsoid(0,0,1,r_bottom, r_bottom, 0, resolution);
    [x_bot, y_bot, z_bot] = ellipsoid(0,0,0,r_top, r_top, 0, resolution);
    X_surf = [x_bot;X;x_top];
    Z_surf = [z_bot;Z;z_top];
    Y_surf = [y_bot;Y;y_top];
    %scale
    X_scale = X_surf * width;
    Y_scale = (Z_surf - 0.5) * height;
    Z_scale = Y_surf * extent;
    %save file
    fvc = surf2patch(X_scale,-1 * Y_scale,Z_scale,'triangles');
    stlwrite(filename, fvc, 'mode', 'ascii')
   
end

function Handle(height, width, extent, curve_factor, resolution, filename)
    % cylinder with offset slices
    resolution_dir = resolution;
    [X,Z,Y] = cylinder(ones(resolution_dir,1), resolution_dir);
    X_scale = X * width;
    Y_scale = Y * height;
    Z_scale = Z * extent/2;

    theta_height = linspace(0, pi, resolution_dir);
    X_offset = X_scale;
    curve_factor = 10;
    for ix = 1:size(X,1)
        X_offset(ix,:) = X_scale(ix, :) + curve_factor*sin(theta_height(ix));
    end

    surf(X_offset, Z_scale, Y_scale)
    xlabel('x'); ylabel('z'); zlabel('y');axis('equal')
    %save file
    fvc = surf2patch(X_offset, Z_scale, Y_scale,'triangles');
    stlwrite(filename, fvc, 'mode', 'ascii')
end

function Vase(height, width, extent, d, resolution, filename) %makes a vase like cup
    % cylinder with a path for the outer dimension
    if width < d
        disp("STL Not Created: Unknown performance.  Width is less than maximum diameter change")
        return
    end
    cylinder_path = 1 - (width - d)/width * sin(linspace(0,pi,resolution));
    [X, Z, Y] = cylinder(cylinder_path, resolution);
    
    %Scale
    X = X * (width/2);
    Y = (Y - 0.5) * (height); % move centroid to origin
    Z = Z * (extent/2);
    %add bottom and top
    [x_end, y_end, z_end] = ellipsoid(0,0,0,width/2, 0, extent/2, resolution);
    y_top = y_end + height/2;
    y_bot = y_end - height/2;
    x_surf = [x_end;X;x_end];
    z_surf = [z_end;Z;z_end];
    y_surf = [y_bot;Y;y_top];
    fvc = surf2patch(x_surf,y_surf,z_surf,'triangles');
    stlwrite(filename, fvc, 'mode', 'ascii')
end