%Description: Create shapes for near contact study and output STL files
close all; clear all;
%%
tmpvol = false(20,20,20); % Empty voxel volume 
tmpvol(8:12,8:12,5:15) = 1; % Turn some voxels on 
fv = isosurface(~tmpvol, 0.5); % Make patch w. faces "out" 
stlwrite('test.stl',fv) % Save to binary .stl 
%%
% % % % Cube Shapes % % % %
%-Parameters
h = 1;
w = 1;
e = 1;
resolution = 10;

% X = [0,1,0];
% Y = [0,1,1];
% Z = [0,1,0; 0,1,0; 0,1,0];
X_span = linspace(0,w,resolution);
Y_span = linspace(0,h,resolution);
Z_span = linspace(0,e,resolution);
one_vec = ones(length(X_span), 1);
X = zeros(length(X_span)*length(Y_span)*6, 1); 
Y = X;
Z = X;
hold on
count = 1;
for ix = 1:length(X_span)
    for iy = 1:length(Y_span)
        for iz = 1:length(Z_span)
            if (iz == 1 || iz == length(Z_span))
                X(count) = X_span(ix); Y(count) = Y_span(iy); Z(count) = Z_span(iz);
            elseif (ix == 1|| ix == length(X_span))
                X(count) = X_span(ix); Y(count) = Y_span(iy); Z(count) = Z_span(iz);
           
            end
%             X(count) = X_span(ix); Y(count) = Y_span(iy); Z(count) = Z_span(end); count = count + 1;
%             X(count) = X_span(1); Y(count) = Y_span(iy); Z(count) = Z_span(ix); count = count + 1;
%             X(count) = X_span(end); Y(count) = Y_span(iy); Z(count) = Z_span(ix); count = count + 1;
%             X(count) = X_span(ix); Y(count) = Y_span(1); Z(count) = Z_span(iy); count = count + 1;
%             X(count) = X_span(ix); Y(count) = Y_span(end); Z(count) = Z_span(iy); count = count + 1;
            count = count + 1;
        end
    end
end
plot3(X, Y, Z, '.')
xlabel('x'); ylabel('y'); zlabel('z');
stlwrite('test.stl',X,Y,Z,'mode','ascii') 
%%

% %-Surface Values
% X_span = [];
% Y_span = [];
% Z_span = [];
% %-- Bottom
% X_span = [X_span, linspace(0, w, resolution)];
% Y_span = [Y_span, linspace(0, h, resolution)];
% Z_span = [Z_span, 0 * ones(length(X_span), length(Y_span))];
% size(Z_span)
% %-- Top
% X_span = [X_span, linspace(0, w, resolution)];
% Y_span = [Y_span, linspace(0, h, resolution)];
% Z_span = [Z_span, e * ones(length(X_span), length(Y_span))];
% 
% [X, Y] = meshgrid(X_span, Y_span);
% Z = e * rand(length(X), length(Y));
% % [X, Y, Z] = ndgrid(X_span, Y_span, Z_span);




[X,Y] = deal(1:40); % Create grid reference 
Z = peaks(40); % Create grid height
hold on
for ix = 1:length(X)
    for iy = 1:length(Y)
        plot3(ix, iy, Z(ix, iy), '.');
    end
end
% surf(X,Y,Z)
% stlwrite('test.stl',X,Y,Z,'mode','ascii') 

%%
%-Parameters
h = 1;
w = 1;
e = 1;
resolution = 10;
X_span = linspace(0,w,resolution);
Y_span = linspace(0,h,resolution);
Z_span = linspace(0,e,resolution);
[X, Y] = meshgrid(X_span, Y_span);
Z_min = Z_span(1) * ones(length(X_span), length(Y_span));
Z_max = Z_span(end) * ones(length(X_span), length(Y_span));
surf([X, X],[Y, Y],[Z, Z+Z_span])
% stlwrite('test.stl',[X, X],[Y, Y],[Z_min, Z_max],'mode','ascii')
%% 
h = 1;
w = 1;
e = 1;
resolution = 10;

V_val = 0.9;
X_span = linspace(0,w,resolution);
Y_span = linspace(0,h,resolution);
Z_span = linspace(0,e,resolution);
[X, Y] = meshgrid(X_span, Y_span);
Z_min = Z_span(1) * ones(length(X_span), length(Y_span));
Z_max = Z_span(end) * ones(length(X_span), length(Y_span));
V = ones(length(X_span), length(X_span), length(Y_span));
V(1,:,:) = V_val; V(end,:,:) = V_val;
V(:,1,:) = V_val; V(:,end,:) = V_val;
V(:,:,1) = V_val; V(:,:,end) = V_val;
fv = isosurface(X_span, Y_span, Z_span, V);
% surf([X, X],[Y, Y],[Z, Z+Z_span])
stlwrite('test.stl', fv, 'mode', 'ascii')

%%
ShapeSTLGenerator('cube', 10, 'cube_test1', 1, 2, 3)
ShapeSTLGenerator('cube', 101, 'cube_test2.stl', 3, 2, 3)

%%
ShapeSTLGenerator('ellipse', 10, 'sphere_test1', 1, 2, 3)
ShapeSTLGenerator('ellipse', 100, 'sphere_test2.stl', 3, 1, 4)

%%
% Cylinder
height = 1; width = 2; extent = 3; resolution = 100;
filename = 'cylinder.stl';
[X, Z, Y] = cylinder(1, resolution);
%Scale
X = X * (width/2);
Y = (Y-0.5) * (height);
Z = Z * (extent/2);
%add bottom and top
[x_bottom, y_end, z_end] = ellipsoid(0,0,0,width/2, 0, extent/2, resolution);
y_top = y_end + height/2;
y_bot = y_end - height/2;
X_surf = [x_bottom;X;x_bottom];
Z_surf = [z_end;Z;z_end];
Y_surf = [y_bot;Y;y_top];
surf(X_surf,Z_surf,Y_surf); xlabel('x');ylabel('z');
% fvc = surf2patch(X_surf,Y_surf,Z_surf,'triangles');
% stlwrite(filename, fvc, 'mode', 'ascii')
% surf([X,x_top],[Y,y_top],[Z,z_top])
% h = get(gca,'DataAspectRatio'); 
% if h(3)==1
%       set(gca,'DataAspectRatio',[1 1 1/max(h(1:2))])
% else
%       set(gca,'DataAspectRatio',[1 1 h(3)])
% end
%% Cylinder
ShapeSTLGenerator('cylinder', 10, 'cylinder_test1', 1, 2, 3)
ShapeSTLGenerator('cylinder', 100, 'cylinder_test2.stl', 3, 1, 4)

%% Cone Explore
height = 1; width = 2; extent = 3; alpha = 10; resolution = 100;
filename = 'cylinder.stl';

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
Y_scale = (Z_surf-0.5) * height;
Z_scale = Y_surf * extent;

% surf(X,Y,Z)
surf(X_scale,Z_scale, Y_scale)
h = get(gca,'DataAspectRatio'); 
if h(3)==1
      set(gca,'DataAspectRatio',[1 1 1/max(h(1:2))])
else
      set(gca,'DataAspectRatio',[1 1 h(3)])
end
xlabel('x'); ylabel('z'); zlabel('y');
%% Cone Test
ShapeSTLGenerator('Cone', 100, 'cone1.stl', 1, 2, 3, 10);

%% Handle
% height = 1; width = 2; extent = 3; alpha = 10; resolution = 100;
% filename = 'handle.stl';
% % create one cylinder
% [X_unit, Z_unit, Y_unit] = cylinder(width, width, height);
% % add cylinder and rotate
% X_surf = []; Y_surf = []; Z_surf = [];
% for i = 1:floor(resolution/10)
%     X_surf
% end

% if i could figure out the function to use with bsxfun then this would be
% the best way to do it!
% r = 0:0.1:pi;
% r = rand(1,10);
r = ones(1,10);
% z = sin(r);
z = linspace(0,1,10);
alpha = 0:0.1:1;
theta = 0:pi/20:2*pi;
xx = bsxfun(@times,r',cos(theta));
yy = bsxfun(@times,r',sin(theta));
zz = repmat(z',1,length(theta));
surf(xx,yy,zz)
axis equal
%%
height = 4; width = 0.5; extent = 0.2; r = 0.1; resolution = 100;
r = ones(1,resolution) * r;
y = linspace(0,1,resolution);
theta_handle = linspace(0,2*pi,resolution);
theta_height = linspace(0,pi, resolution);
% make handle shape
XX = zeros(length(r), length(theta_handle));
ZZ = zeros(length(r), length(theta_handle));
YY = repmat(y',1,length(theta_handle));
for i1 = 1:length(r)
    for i2 = 1:length(theta_handle)
        XX(i1,i2) = cos(theta_handle(i2)) + width/r(1) * sin(theta_height(i1));
        ZZ(i1,i2) = sin(theta_handle(i2));
    end
end
%add top and bottom
[x_end, y_end, z_end] = ellipsoid(0,0,0,1, 0, 1, resolution-1);
XX_surf = [x_end; XX; x_end];
y_top = y_end + 1;
YY_surf = [y_end; YY; y_top];
ZZ_surf = [z_end; ZZ; z_end];
figure(1); surf(XX_surf,ZZ_surf,YY_surf); axis equal; figure(2);
ZZ_scale = ZZ_surf * extent;
XX_scale = XX_surf * r(1);
YY_scale = YY_surf * height;
surf(XX_scale,ZZ_scale,YY_scale)
axis equal

%% Handle Test
ShapeSTLGenerator('handle', 100, 'handle1.stl', 5, 0.5, 0.5, 0.1);
ShapeSTLGenerator('handle', 100, 'handle2', 5, 0.2, 0.1, 0.5);



