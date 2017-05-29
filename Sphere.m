function Sphere(height, width, extent, resolution, filename)
%Description: Create sphere STL object
%Author: Ammar Kothari 5/21/17
%Inputs: features of sphere and number of points in each direction, filename
%to save file to
%Output: none
%saves STL to file
  
    xc = 0;
    yc = 0;
    zc = 0;
    xr = width;
    yr = height/2;
    zr = extent/2;
    n = resolution;
    [x,y,z] = ellipsoid(xc,yc,zc,xr,yr,zr,n);
    fvc = surf2patch(x,y,z,'triangles');
    if isempty(strfind(filename,'.stl'))
        fname = strcat(filename,'.stl');
    else
        fname = filename;
    end
    stlwrite(filename, fvc, 'mode', 'ascii')
end