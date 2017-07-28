function fn_save = MakeShapeFileName(sprintf_string, cell_values)
% function to create filenames for saving files
% system started to breakdown once decimals were used, so needed additional
% control/adjustment beyond basic sprintf

% check if there are enough values?

% if value is greater than 1, then show value
% if value is less than 1, have a leading zero

str_split = split(sprintf_string, '%');

for iv = 1:size(cell_values,2)
    if isstr(cell_values{iv})
        % don't do anything
        continue
    else
        if mod(cell_values{iv}, 1) ~= 0 %have to deal with decimals!
            str_split{iv+1} = replace(str_split{iv+1}, 'd','0.1f');
        elseif  mod(cell_values{iv}, 1) == 0
            % don't have to do anything because it should already be %d
            continue
            
        end
    end
end
sprintf_save = join(str_split, '%');
fn_save = sprintf(sprintf_save{1}, cell_values{:});

fn_save = replace(fn_save, '.', 'D');




end