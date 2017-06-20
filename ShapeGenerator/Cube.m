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
    if (length(filename) <= 4) || ~strcmp(filename(end-4:-1),'.stl')
        fname = strcat(filename,'.stl');
    else
        fname = filename;
    end
    stlwrite(fname, fv, 'mode', 'ascii')



end