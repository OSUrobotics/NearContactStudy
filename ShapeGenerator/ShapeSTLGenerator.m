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
    V_val = true;
    X_span = linspace(-1,1,resolution);
    Y_span = linspace(-1,1,resolution);
    Z_span = linspace(-1,1,resolution);
    V = V_val * zeros(resolution, resolution, resolution);
    V(1,:,:) = V_val; V(end,:,:) = V_val;
    V(:,1,:) = V_val; V(:,end,:) = V_val;
    V(:,:,1) = V_val; V(:,:,end) = V_val;
    fv = isosurface(X_span, Y_span, Z_span, V);
    fv.vertices(:,1) = fv.vertices(:,1) / max(fv.vertices(:,1)) * width/2;
    fv.vertices(:,2) = fv.vertices(:,2) / max(fv.vertices(:,2)) * height/2;
    fv.vertices(:,3) = fv.vertices(:,3) / max(fv.vertices(:,3)) * extent/2;
    stlwrite(filename, fv, 'mode', 'ascii')
end

function Ellipse(height, width, extent, resolution, filename)
    xc = 0;
    yc = 0;
    zc = 0;
    xr = width/2;
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

function Cone(height, width, extent, p_cutoff, resolution, filename)
    % p_cutoff is the percent amount of the top of the cone that is chopped off
    t = linspace(0,2*pi, resolution);
    X_lower = width/2 * sin(t);
    Z_lower = extent/2 * cos(t);
    Y_lower = -height/2*ones(1, resolution);
    height_complete = height / (1 - p_cutoff);
    w_gamma = atan2(width/2, height_complete);
    e_gamma = atan2(extent/2, height_complete);
    w_upper = 2*(width/2 - height*tan(w_gamma));
    e_upper = 2*(extent/2 - height*tan(e_gamma));
    X_upper = w_upper/2 * sin(t);
    Z_upper = e_upper/2 * cos(t);
    Y_upper = height/2*ones(1, resolution);
    [x_bottom, z_bottom, y_bottom] = ellipsoid(0,0,-height/2,width/2, extent/2, 0, resolution-1);
    [x_top, z_top, y_top] = ellipsoid(0,0,height/2,w_upper/2, e_upper/2, 0, resolution-1);
    X = [x_bottom; X_lower; X_upper; x_top];
    Z = [z_bottom; Z_lower; Z_upper; z_top];
    Y = [y_bottom; Y_lower; Y_upper; y_top];
    fvc = surf2patch(X,-1*Y,Z,'triangles');
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