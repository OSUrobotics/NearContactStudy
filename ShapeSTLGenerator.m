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
    elseif strcmpi(shape_type, 'handle')
    	Handle(height, width, extent, alpha, resolution, filename)
        disp('Creating Handle')
    elseif  strcmpi(shape_type, 'handle') && isnan(alpha)
        disp('Need alpha to create handle');
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
    X_span = linspace(0,width,resolution);
    Y_span = linspace(0,height,resolution);
    Z_span = linspace(0,extent,resolution);
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
    Y = Y * (height);
    Z = Z * (extent/2);
    %add bottom and top
    [x_end, y_end, z_end] = ellipsoid(0,0,0,width/2, 0, extent/2, resolution);
    y_top = y_end + height;
    y_bot = y_end;
    x_surf = [x_end;X;x_end];
    z_surf = [z_end;Z;z_end];
    y_surf = [y_bot;Y;y_top];
    surf(x_surf,z_surf,y_surf); xlabel('x');ylabel('z');
    fvc = surf2patch(x_surf,y_surf,z_surf,'triangles');
    stlwrite(filename, fvc, 'mode', 'ascii')

end

function Cone(height, width, extent, alpha, resolution, filename)
    % unit cone with specified alpha
    r_bottom = 0.5;
    r_top = 0.5 - sind(alpha);
    [X, Y, Z] = cylinder([r_bottom, r_top], resolution);
    %add top and bottom;
    [x_bot, y_bot, z_bot] = ellipsoid(0,0,0,r_bottom, r_bottom, 0, resolution);
    [x_top, y_top, z_top] = ellipsoid(0,0,height,r_top, r_top, 0, resolution);
    X_surf = [x_bot;X;x_top];
    Z_surf = [z_bot;Z;z_top];
    Y_surf = [y_bot;Y;y_top];
    %scale
    X_scale = X_surf * width;
    Y_scale = Z_surf * height;
    Z_scale = Y_surf * extent;
    %save file
    fvc = surf2patch(X_scale,Y_scale,Z_scale,'triangles');
    stlwrite(filename, fvc, 'mode', 'ascii')
   
end

function Handle(height, width, extent, r, resolution, filename)
    r = ones(1,resolution) * r;
    y = linspace(0,1,resolution);
    theta_handle = linspace(0,2*pi,resolution);
    theta_height = linspace(0,pi, resolution);
    % make handle shape
    X = zeros(length(r), length(theta_handle));
    Z = zeros(length(r), length(theta_handle));
    Y = repmat(y',1,length(theta_handle));
    for i1 = 1:length(r)
        for i2 = 1:length(theta_handle)
            X(i1,i2) = cos(theta_handle(i2)) + width/r(1) * sin(theta_height(i1));
            Z(i1,i2) = sin(theta_handle(i2));
        end
    end
    %add top and bottom
    [x_end, y_end, z_end] = ellipsoid(0,0,0,1, 0, 1, resolution-1);
    X_surf = [x_end; X; x_end];
    y_top = y_end + 1;
    Y_surf = [y_end; Y; y_top];
    Z_surf = [z_end; Z; z_end];
    %scale to size
    Z_scale = Z_surf * extent;
    X_scale = X_surf * r(1);
    Y_scale = Y_surf * height;
    % save file
    %save file
    fvc = surf2patch(X_scale,Y_scale,Z_scale,'triangles');
    stlwrite(filename, fvc, 'mode', 'ascii')
end