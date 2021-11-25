i_par = 4;
hand = "R";
run =1;
med="MedOn";
cond = logical(mod(i_par,2));
conditions = ["Fast-Slow","Slow-Fast"];
i_par = sprintf("0%i",i_par);
file_name = strcat("sub-",string(i_par),"-",med,"-task-VigorStim",hand,...
            "-", conditions(cond+1),"-StimOn","-run-0",string(run),...
            "-behavioral.mat");

%Put all the data into one structure
struct.options = options;
struct.data = data;
save(strcat(pwd,'/Data/Parkinson/',file_name), "struct");