addpath C:\TMSi;addpath C:\CODE\wjn_toolbox\;
%% INITIALIZE TMSI
close all;clear all;try AO_CloseConnection(); poly5.close(); end, try  sampler.stop(); end;try  sampler.disconnect(); end, try  library.destroy(); end;clear all

%% OPTIONS
thisorder = randi(4);
allorders = [1 2 3 4; 3 4 1 2 ; 2 1 4 3; 3 1 4 2];
allconditions = {'x*side<0 && abs(xvel)>xthresh && ~stim && bstim~=b','x*side<0 && abs(xvel)<xthresh && ~stim && bstim~=b','x*side<0 && abs(yvel)>ythresh && ~stim && bstim~=b','x*side<0 && abs(yvel)<ythresh && ~stim && bstim~=b'};
options.filename = 'tt';
options.ntrials = 50;
options.nblocks = 9;
options.target_size_x = 100;
options.target_size_y = 140;
options.target_distance_x = 640;
options.target_distance_y = 0;
options.target_distance_y_jitter = 300;
options.cursor_stay_time = 0.25;
options.cursor_stay_time_jitter = 0.25;
options.stim_threshold = 50;
options.stim = 1;
options.stim_channel = 1;
options.stim_return_channel=-1;
options.stim_amp=[0 .7];
options.stim_duration = 0.3;
options.stim_hz=130;
options.stim_pw=60;
% options.stim_condition = {'0','abs(vel)>thresh && ~stim','0','abs(vel)<thresh && ~stim','0'};     
options.stim_condition = {'0',allconditions{allorders(thisorder,1)},'0',allconditions{allorders(thisorder,2)},'0',allconditions{allorders(thisorder,3)},'0',allconditions{allorders(thisorder,1)},'0'};     
options.system = '';

%% INITIALIZE TMSI
if strcmp(options.system,'tmsi')
    [sampler,poly5,channels,device,fs,library,t_init]=wjn_tmsi_initialize(options.filename);
    sys=1;
elseif strcmp(options.system,'AO')
    sys=2;
    [channels,fs]=wjn_init_AO('test',1,1:16);
else
    sys=0;
end
%% INITIALIZE VARIABLES
t0=tic;tlast=tic;tstim=tic;bstim=0;
target=0;xvel=0;yvel=0;stim=0;
side = 1;
ctarget = [options.target_distance_x 0];
data = nan(60,12);
figure
subplot(1,2,1)
bvel=plot(linspace(-1,0,60),data(:,4),'linewidth',2);
hold on
bthresh=plot([-1 1],[nan nan],'linestyle','--','linewidth',1.5);
bax=gca;
xlim([-1 0]);
subplot(1,2,2)
bc=scatter(nan,nan,'filled');
xlim([-640 640]);ylim([-512 512]);
figone(5,10)
drawnow


%% INITIALIZE COGENT
clc
cgloadlib
cgopen(5,0,0,1);
cgalign('c','c')
cgfont('Arial',30);
cgpencol(1,1,1);
km = cgkeymap;

%% START TRIALS

for a = 1:options.nblocks
    if a==1
        while (~km(1) && ~km(28) && ~km(57));km=cgkeymap;cgtext('Start?',0,50);cgrect(ctarget(1),ctarget(2),options.target_size_x,options.target_size_y,[1 0 0]);cgflip(0,0,0);        end
    elseif a==round(options.nblocks/2)
        while (~km(1) && ~km(28) && ~km(57));km=cgkeymap;cgtext('Pause?',0,50);cgflip(0,0,0);end
    end

    disp(['Block: ' num2str(a) ' ' options.stim_condition{a}])
    for b = 1:options.ntrials
        cumxvel=0;
        cumyvel=0;
        side=side*-1;nexttarget=0;ttarget=0;ttrial=tic;
        ctarget = [options.target_distance_x*side options.target_distance_y+((rand-.5)*options.target_distance_y_jitter)];       
        while ~nexttarget
            km=cgkeymap;[x,y]=cgmouse;
            dist=abs([x-ctarget(1) y-ctarget(2)]);target=dist(1)<options.target_size_x/2 && dist(2)<options.target_size_y/2;
            xvel=nanmean(abs(diff(data(end-2:end,2))));
            yvel=nanmean(abs(diff(data(end-2:end,3))));
            if ~target && x.*side<0
                cumxvel=cumxvel+xvel;
                cumyvel=cumyvel+yvel;             
            end
            ndata = [toc(t0) x y xvel yvel side target a b stim cumxvel cumyvel];
            data = [data;ndata];
            
            if b>2
                mxvel(a,b)=nansum(abs(data(data(:,9)==b-1&data(:,7)==0&data(:,2).*side<0,4)));
                myvel(a,b)=nansum(abs(data(data(:,9)==b-1&data(:,7)==0&data(:,2).*side<0,5)));
            else
                mxvel(a,b) = nan;
                myvel(a,b) = nan;
            end
            if a >1
                xthresh = prctile(mxvel(1,:),options.stim_threshold);
                ythresh = prctile(myvel(1,:),options.stim_threshold);
                bthresh.YData=[xthresh xthresh];
%                 bax.YLim = [0 3*xthresh];
%                 disp([x*side abs(xvel) xthresh stim])
                if eval(options.stim_condition{a})
                    wjn_stim_AO([1 options.stim],options.stim_channel,options.stim_amp,0,options.stim_duration,options.stim_return_channel,options.stim_hz,options.stim_pw,1);
                    stim = 1;
                    bstim = b;
                    tstim=tic;
                elseif ~stim || toc(tstim)>options.stim_duration
                    stim=0;
                end
            end
            
            if size(data,1)>120 && toc(tlast)>.25
                set(bax.Title,'String',num2str(diff(data(end-1:end,1)),2));
                bvel.YData = abs(data(end-59:end,4));drawnow;
                bc.XData = x;
                bc.YData = y;
                tlast=tic;
            end
            if ~target
                cgpencol(0,.5,.5);
            elseif target && ~ttarget
                ttarget = tic;cgpencol(.5,0,.5)
            else       
                if toc(ttarget)>(options.cursor_stay_time+rand*options.cursor_stay_time_jitter)
                    nexttarget=1;
                end
            end
            cgrect(ctarget(1),ctarget(2),options.target_size_x,options.target_size_y);
%             cgpencol(1,1,1)
            cgellipse(x,y,5,5,'f')
            cgflip(0,0,0);
            if km(1)
                pause(.1);km=cgkeymap;
                while (~km(1) && ~km(28) && ~km(57));km=cgkeymap;cgtext('Abbrechen?',0,50);cgflip(0,0,0);end
                if km(1);cgshut;return;end
            end
     
        end
    end
end
cgshut

