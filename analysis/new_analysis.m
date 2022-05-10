addpath ..\wjn_toolbox


%% 

%% trials x condition x recordings
% Block 1: 1:96 Stim
% Block 2: 97:192 Recovery
% Condition 1: Slow
% Condition 2: Fast
% Recordings: 
%     {'sub-01-MedOff-task-VigorStim-R-Slow-Fast-StimOn-run-01-behavioral.mat'}
%     {'sub-02-MedOff-task-VigorStim-R-Fast-Slow-StimOn-run-01-behavioral.mat'}
%     {'sub-03-MedOff-task-VigorStim-R-Fast-Slow-StimOn-run-01-behavioral.mat'}
%     {'sub-03-MedOn-task-VigorStim-L-Fast-Slow-StimOn-run-01-behavioral.mat' }
%     {'sub-03-MedOn-task-VigorStim-R-Slow-Fast-StimOn-run-01-behavioral.mat' }
%     {'sub-04-MedOn-task-VigorStim-R-Fast-Slow-StimOn-run-01-behavioral.mat' }
%     {'sub-05-MedOff-task-VigorStim-R-Slow-Fast-StimOn-run-01_behavioral.mat'}
%     {'sub-05-MedOff-task-VigorStim-R-Slow-Fast-StimOn-run-02_behavioral.mat'}
%     {'sub-06-MedOff-task-VigorStim-R-Fast-Slow-StimOn-run-01_behavioral.mat'}
%     {'sub-06-MedOn-task-VigorStim-R-Fast-Slow-StimOn-run-01_behavioral.mat' }
%     {'sub-07-MedOn-task-VigorStim-R-Slow-Fast-StimOn-run-01-behavioral.mat'}
%     {'sub-08-MedOff-task-VigorStim-R-Fast-Slow-StimOn-run-01-behavioral.mat'}
%     {'sub-08-MedOn-task-VigorStim-R-Fast-Slow-StimOn-run-01-behavioral.mat'}
%     {'sub-09-MedOff-task-VigorStim-R-Slow-Fast-StimOn-run-01-behavioral.mat'}
%     {'sub-10-MedOff-task-VigorStim-L-Fast-Slow-StimOn-run-01-behavioral.mat'}



%% All patients
clear all, close all
load peak_velocities_raw.mat
ipat = [1 2 3 4 5 6 7 8 9 10 11 12 13 14 15];
cmap = wjn_erc_colormap
col_fast = [0.4940, 0.1840, 0.5560];
col_slow = [0.4660, 0.6740, 0.1880];

nr=5;
sk=5;
nn=1:5;
sfs=[];sfr=[];sss=[];ssr=[];asfs=[];asfr=[];asss=[];assr=[];psfs=[];psfr=[];psss=[];pssr=[];
fast_trials_stim = squeeze(peaks_all_raw(nr+1:96-nr,2,ipat));
slow_trials_stim = squeeze(peaks_all_raw(nr+1:96-nr,1,ipat));
fast_trials_rec = squeeze(peaks_all_raw(nr+97:192-nr,2,ipat));
slow_trials_rec = squeeze(peaks_all_raw(nr+97:192-nr,1,ipat));
for a = 1:length(ipat)
    sfs(a,:) = smooth(fast_trials_stim(:,a),sk);
    sss(a,:) = smooth(slow_trials_stim(:,a),sk);
    sfr(a,:) = smooth(fast_trials_rec(:,a),sk);  
    ssr(a,:) = smooth(slow_trials_rec(:,a),sk); 
    
   
    asfs(a,:) = sfs(a,:)-nanmean(sfs(a,nn));
    asfr(a,:) = sfr(a,:)-nanmean(sfs(a,nn));
    asss(a,:) = sss(a,:)-nanmean(sss(a,nn));
    assr(a,:) = ssr(a,:)-nanmean(sss(a,nn));
    
        
    psfs(a,:) = (sfs(a,:)-nanmean(sfs(a,nn)))./nanmean(sfs(a,nn)).*100;
    psfr(a,:) = (sfr(a,:)-nanmean(sfs(a,nn)))./nanmean(sfs(a,nn)).*100;
    psss(a,:) = (sss(a,:)-nanmean(sss(a,nn)))./nanmean(sss(a,nn)).*100;
    pssr(a,:) = (ssr(a,:)-nanmean(sss(a,nn)))./nanmean(ssr(a,nn)).*100;
end

for a = 1:size(sfs,2)
    astim(a) = wjn_ppt(asfs(:,a),asss(:,a));
    arec(a) = wjn_ppt(asfr(:,a),assr(:,a));
    pstim(a) = wjn_ppt(psfs(:,a),psss(:,a));
    prec(a) = wjn_ppt(psfr(:,a),pssr(:,a));
end

ts = 1:size(sfs,2);
tr = size(sfs,2)+1:size(sfs,2)+size(sfr,2);

figure
subplot(2,2,1)
mypower(ts,asfs,col_fast,'sem')
ylim([-1500 1500]/2)
hold on
mypower(ts,asss,col_slow,'sem')
% %sigbar(ts,astim<=0.05)
mypower(ts,asfs,col_fast,'sem')
hold on
mypower(ts,asss,col_slow,'sem')
title('Stimulation')
box off
ylabel('Movement velocity [p/s]')
xlabel('Trial')

subplot(2,2,2)
mypower(tr,asfr,col_fast,'sem')
hold on
ylim([-1500 1500]/2)
mypower(tr,assr,col_slow,'sem')
% %sigbar(tr,arec<=0.05)
mypower(tr,asfr,col_fast,'sem')
hold on
mypower(tr,assr,col_slow,'sem')
title('Recovery')
box off
set(gca,'YTick',[])
xlabel('Trial')
figone(7,20)


subplot(2,2,3)
mypower(ts,psfs,col_fast,'sem')
ylim([-20 20])
hold on
mypower(ts,psss,col_slow,'sem')
% %sigbar(ts,pstim<=0.05)
mypower(ts,psfs,col_fast,'sem')
hold on
mypower(ts,psss,col_slow,'sem')
title('Stimulation')
box off
ylabel('Movement velocity [%]')
xlabel('Trial')

subplot(2,2,4)
mypower(tr,psfr,col_fast,'sem')
hold on
ylim([-20 20])
mypower(tr,pssr,col_slow,'sem')
% %sigbar(tr,prec<=0.05)
mypower(tr,psfr,col_fast,'sem')
hold on
mypower(tr,pssr,col_slow,'sem')
title('Recovery')
box off
set(gca,'YTick',[])
xlabel('Trial')
figone(10,20)

%%

%% All sessions
clear all, close all
cmap = wjn_erc_colormap
load peak_velocities_raw.mat
ipat = [1 2 3 4 5 6 7 8 9 10 11 12 13 14 15];
col_fast = [0.4940, 0.1840, 0.5560];
col_slow = [0.4660, 0.6740, 0.1880];

nr=5;
sk=5;
nn=1:5;
sfs=[];sfr=[];sss=[];ssr=[];asfs=[];asfr=[];asss=[];assr=[];psfs=[];psfr=[];psss=[];pssr=[];
fast_trials_stim = squeeze(peaks_all_raw(nr+1:96-nr,2,ipat));
slow_trials_stim = squeeze(peaks_all_raw(nr+1:96-nr,1,ipat));
fast_trials_rec = squeeze(peaks_all_raw(nr+97:192-nr,2,ipat));
slow_trials_rec = squeeze(peaks_all_raw(nr+97:192-nr,1,ipat));
for a = 1:length(ipat)
    sfs(a,:) = smooth(fast_trials_stim(:,a),sk);
    sss(a,:) = smooth(slow_trials_stim(:,a),sk);
    sfr(a,:) = smooth(fast_trials_rec(:,a),sk);  
    ssr(a,:) = smooth(slow_trials_rec(:,a),sk); 
    
   
    asfs(a,:) = sfs(a,:)-nanmean(sfs(a,nn));
    asfr(a,:) = sfr(a,:)-nanmean(sfs(a,nn));
    asss(a,:) = sss(a,:)-nanmean(sss(a,nn));
    assr(a,:) = ssr(a,:)-nanmean(sss(a,nn));
    
        
    psfs(a,:) = (sfs(a,:)-nanmean(sfs(a,nn)))./nanmean(sfs(a,nn)).*100;
    psfr(a,:) = (sfr(a,:)-nanmean(sfs(a,nn)))./nanmean(sfs(a,nn)).*100;
    psss(a,:) = (sss(a,:)-nanmean(sss(a,nn)))./nanmean(sss(a,nn)).*100;
    pssr(a,:) = (ssr(a,:)-nanmean(sss(a,nn)))./nanmean(ssr(a,nn)).*100;
end

for a = 1:size(sfs,2)
    astim(a) = wjn_ppt(asfs(:,a),asss(:,a));
    arec(a) = wjn_ppt(asfr(:,a),assr(:,a));
    pstim(a) = wjn_ppt(psfs(:,a),psss(:,a));
    prec(a) = wjn_ppt(psfr(:,a),pssr(:,a));
end

ts = 1:size(sfs,2);
tr = size(sfs,2)+1:size(sfs,2)+size(sfr,2);

figure
subplot(1,2,1)
mypower(ts,asfs,col_fast,'sem')
ylim([-1500 1500]/2)
hold on
mypower(ts,asss,col_slow,'sem')
%sigbar(ts,astim<=0.05)
mypower(ts,asfs,col_fast,'sem')
hold on
mypower(ts,asss,col_slow,'sem')
title('Stimulation')
box off
ylabel('Movement velocity [p/s]')
xlabel('Trial')

subplot(1,2,2)
mypower(tr,asfr,col_fast,'sem')
hold on
ylim([-1500 1500]/2)
mypower(tr,assr,col_slow,'sem')
%sigbar(tr,arec<=0.05)
mypower(tr,asfr,col_fast,'sem')
hold on
mypower(tr,assr,col_slow,'sem')
title('Recovery')
box off
set(gca,'YTick',[])
xlabel('Trial')
figone(7,20)

ib = [1:size(assr,2)./2 ;1+size(assr,2)./2:size(assr,2)];
fast_block = [nanmean(asfs(:,ib(1,:)),2) nanmean(asfs(:,ib(2,:)),2) nanmean(asfr(:,ib(1,:)),2) nanmean(asfr(:,ib(1,:)),2)];
slow_block = [nanmean(asss(:,ib(1,:)),2) nanmean(asss(:,ib(2,:)),2) nanmean(assr(:,ib(1,:)),2) nanmean(assr(:,ib(1,:)),2)];

for a = 1:4
    p0f(1,a) = wjn_pt(fast_block(:,a));
    p0s(1,a) = wjn_pt(slow_block(:,a));
    psf(1,a) = wjn_pt(fast_block(:,a),slow_block(:,a));
end
  
figure
b1=mybar(fast_block,col_fast,[1:4]-.1,.25);
hold on 
b2=mybar(slow_block,col_slow,[1:4]+.1,.25);
xlim([.5 4.5])
set(gca,'XTickLabels',{'1st 1/2','2nd 1/2','1st 1/2','2nd half'})
xlabel('Stimulation block         Recovery block')
ylabel('Velocity [p/s]')
sigbracket('p=0.01',3,900,9)
sigbracket('p=0.01',4,900,9)
sigbracket('p=0.07',2,900,9)
ylim([-1300 1300])
legend([b1(1) b2(1)],{'Fast','Slow'},'Location','NorthEastOutside')
figone(7,10)
title({['N = ' num2str(size(fast_block,1)) ' sessions from 6 PD patients'],'Movement velocity adapted DBS'})

figone(7,40)
myprint('one_session_per_patient')
%% One session per patient
clear all, close all
load peak_velocities_raw.mat
ipat = [1 2 3  6 7 9 11 12 14 15];
cmap = wjn_erc_colormap;
col_fast = [0.4940, 0.1840, 0.5560];
col_slow = [0.4660, 0.6740, 0.1880];

nr=5;
sk=5;
nn=1:5;
sfs=[];sfr=[];sss=[];ssr=[];asfs=[];asfr=[];asss=[];assr=[];psfs=[];psfr=[];psss=[];pssr=[];
fast_trials_stim = squeeze(peaks_all_raw(nr+1:96-nr,2,ipat));
slow_trials_stim = squeeze(peaks_all_raw(nr+1:96-nr,1,ipat));
fast_trials_rec = squeeze(peaks_all_raw(nr+97:192-nr,2,ipat));
slow_trials_rec = squeeze(peaks_all_raw(nr+97:192-nr,1,ipat));
for a = 1:length(ipat)
    sfs(a,:) = smooth(fast_trials_stim(:,a),sk);
    sss(a,:) = smooth(slow_trials_stim(:,a),sk);
    sfr(a,:) = smooth(fast_trials_rec(:,a),sk);  
    ssr(a,:) = smooth(slow_trials_rec(:,a),sk); 
    
   
    asfs(a,:) = sfs(a,:)-nanmean(sfs(a,nn));
    asfr(a,:) = sfr(a,:)-nanmean(sfs(a,nn));
    asss(a,:) = sss(a,:)-nanmean(sss(a,nn));
    assr(a,:) = ssr(a,:)-nanmean(sss(a,nn));
    
        
    psfs(a,:) = (sfs(a,:)-nanmean(sfs(a,nn)))./nanmean(sfs(a,nn)).*100;
    psfr(a,:) = (sfr(a,:)-nanmean(sfs(a,nn)))./nanmean(sfs(a,nn)).*100;
    psss(a,:) = (sss(a,:)-nanmean(sss(a,nn)))./nanmean(sss(a,nn)).*100;
    pssr(a,:) = (ssr(a,:)-nanmean(sss(a,nn)))./nanmean(ssr(a,nn)).*100;
end

for a = 1:size(sfs,2)
    astim(a) = wjn_ppt(asfs(:,a),asss(:,a));
    arec(a) = wjn_ppt(asfr(:,a),assr(:,a));
    pstim(a) = wjn_ppt(psfs(:,a),psss(:,a));
    prec(a) = wjn_ppt(psfr(:,a),pssr(:,a));
end

ts = 1:size(sfs,2);
tr = size(sfs,2)+1:size(sfs,2)+size(sfr,2);


figure
subplot(1,3,1)
mypower(ts,asfs,col_fast,'sem')
ylim([-1700 1700]/2)
hold on
mypower(ts,asss,col_slow,'sem')
%sigbar(ts,astim<=0.05)
mypower(ts,asfs,col_fast,'sem')
hold on
mypower(ts,asss,col_slow,'sem')
title('Stimulation')
box off
ylabel('Movement velocity [p/s]')
xlabel('Trial')

subplot(1,3,2)
mypower(tr,asfr,col_fast,'sem')
hold on
ylim([-1700 1700]/2)
mypower(tr,assr,col_slow,'sem')
%sigbar(tr,arec<=0.05)
mypower(tr,asfr,col_fast,'sem')
hold on
mypower(tr,assr,col_slow,'sem')
title('Recovery')
box off
set(gca,'YTick',[])
xlabel('Trial')

% myprint('one_session_per_patient')

ib = [1:size(assr,2)./2 ;1+size(assr,2)./2:size(assr,2)];
fast_block = [nanmean(asfs(:,ib(1,:)),2) nanmean(asfs(:,ib(2,:)),2) nanmean(asfr(:,ib(1,:)),2) nanmean(asfr(:,ib(1,:)),2)];
slow_block = [nanmean(asss(:,ib(1,:)),2) nanmean(asss(:,ib(2,:)),2) nanmean(assr(:,ib(1,:)),2) nanmean(assr(:,ib(1,:)),2)];

for a = 1:4
    p0f(1,a) = wjn_pt(fast_block(:,a));
    p0s(1,a) = wjn_pt(slow_block(:,a));
    psf(1,a) = ttestp(fast_block(:,a),slow_block(:,a),0.05,'right');
end
  


subplot(1,3,3)
b1=mybar(fast_block,col_fast,[1:4]-.1,.25);
hold on 
b2=mybar(slow_block,col_slow,[1:4]+.1,.25);
xlim([.5 4.5])
set(gca,'XTickLabels',{'1st 1/2','2nd 1/2','1st 1/2','2nd half'})
xlabel('Stimulation block         Recovery block')
ylabel('\Delta Velocity [p/s]')
sigbracket('p=0.04',2,900,9)
sigbracket('p=0.01',4,1350,9)
sigbracket('p=0.01',3,1350,9)
ylim([-1700 1700])
legend([b1(1) b2(1)],{'Fast','Slow'},'Location','NorthEastOutside')

title({['N = ' num2str(size(fast_block,1)) ' sessions from 6 PD patients'],'Movement velocity adapted DBS'})

figone(7,40)
myprint('one_session_per_patient')

T = array2table([ts' asfs' asss' asfr' assr'],'VariableNames',{'Trial','Stim_Fast_sub001','Stim_Fast_sub002','Stim_Fast_sub003','Stim_Fast_sub004','Stim_Fast_sub005','Stim_Fast_sub006' 'Stim_Slow_sub001','Stim_Slow_sub002','Stim_Slow_sub003','Stim_Slow_sub004','Stim_Slow_sub005','Stim_Slow_sub006' 'Recovery_Fast_sub001','Recovery_Fast_sub002','Recovery_Fast_sub003','Recovery_Fast_sub004','Recovery_Fast_sub005','Recovery_Fast_sub006' 'Recovery_Slow_sub001','Recovery_Slow_sub002','Recovery_Slow_sub003','Recovery_Slow_sub004','Recovery_Slow_sub005','Recovery_Slow_sub006'});
writetable(T,'Vigorstim_6pat.csv')
mT = array2table([ts' nanmean(asfs',2) nanmean(asss',2) nanmean(asfr',2) nanmean(assr',2)],'VariableNames',{'Trial','Stim_Fast_Mean', 'Stim_Slow_Mean','Recovery_Fast_Mean','Recovery_Slow_Mean'});
writetable(mT,'Vigorstim_6pat_mean.csv')



%% One session per patient / printed as percentage
clear all, close all
load peak_velocities_raw.mat
ipat = [1 2 3  6 7 9 ];
cmap = wjn_erc_colormap;
col_fast = [0.4940, 0.1840, 0.5560];
col_slow = [0.4660, 0.6740, 0.1880];
col_fast = cmap(2,:);
col_slow = cmap(1,:);

nr=5;
sk=5;
nn=1:5;
sfs=[];sfr=[];sss=[];ssr=[];asfs=[];asfr=[];asss=[];assr=[];psfs=[];psfr=[];psss=[];pssr=[];
fast_trials_stim = squeeze(peaks_all_raw(nr+1:96-nr,2,ipat));
slow_trials_stim = squeeze(peaks_all_raw(nr+1:96-nr,1,ipat));
fast_trials_rec = squeeze(peaks_all_raw(nr+97:192-nr,2,ipat));
slow_trials_rec = squeeze(peaks_all_raw(nr+97:192-nr,1,ipat));
for a = 1:length(ipat)
    sfs(a,:) = smooth(fast_trials_stim(:,a),sk);
    sss(a,:) = smooth(slow_trials_stim(:,a),sk);
    sfr(a,:) = smooth(fast_trials_rec(:,a),sk);  
    ssr(a,:) = smooth(slow_trials_rec(:,a),sk); 
    
   
    asfs(a,:) = sfs(a,:)-nanmean(sfs(a,nn));
    asfr(a,:) = sfr(a,:)-nanmean(sfs(a,nn));
    asss(a,:) = sss(a,:)-nanmean(sss(a,nn));
    assr(a,:) = ssr(a,:)-nanmean(sss(a,nn));
    
        
    psfs(a,:) = (sfs(a,:)-nanmean(sfs(a,nn)))./nanmean(sfs(a,nn)).*100;
    psfr(a,:) = (sfr(a,:)-nanmean(sfs(a,nn)))./nanmean(sfs(a,nn)).*100;
    psss(a,:) = (sss(a,:)-nanmean(sss(a,nn)))./nanmean(sss(a,nn)).*100;
    pssr(a,:) = (ssr(a,:)-nanmean(sss(a,nn)))./nanmean(ssr(a,nn)).*100;
end

for a = 1:size(sfs,2)
    astim(a) = wjn_ppt(asfs(:,a),asss(:,a));
    arec(a) = wjn_ppt(asfr(:,a),assr(:,a));
    pstim(a) = wjn_ppt(psfs(:,a),psss(:,a));
    prec(a) = wjn_ppt(psfr(:,a),pssr(:,a));
end

ts = 1:size(sfs,2);
tr = size(sfs,2)+1:size(sfs,2)+size(sfr,2);


figure
subplot(1,3,1)
mypower(ts,psfs,[0.4940, 0.1840, 0.5560],'sem')
hold on 
yline(0, "LineWidth", 1.5)
ylim([-30 30])
hold on
mypower(ts,psss,col_slow,'sem')
%sigbar(ts,astim<=0.05)
mypower(ts,psfs,col_fast,'sem')
hold on
mypower(ts,psss,col_slow,'sem')
title('Stimulation')
box off
ylabel('\Delta Movement speed [%]')
xlabel('Trial')

subplot(1,3,2)
mypower(tr,psfr,col_fast,'sem')
hold on
ylim([-30 30])
mypower(tr,pssr,col_slow,'sem')
hold on 
yline(0, "LineWidth", 1.5)
%sigbar(tr,arec<=0.05)
mypower(tr,psfr,col_fast,'sem')
hold on
mypower(tr,pssr,col_slow,'sem')
title('No Stimulation (Recovery)')
box off
set(gca,'YTick',[])
xlabel('Trial')

% myprint('one_session_per_patient')

ib = [1:size(pssr,2)./2 ;1+size(pssr,2)./2:size(pssr,2)];
fast_block = [nanmean(psfs(:,ib(1,:)),2) nanmean(psfs(:,ib(2,:)),2) nanmean(psfr(:,ib(1,:)),2) nanmean(psfr(:,ib(1,:)),2)];
slow_block = [nanmean(psss(:,ib(1,:)),2) nanmean(psss(:,ib(2,:)),2) nanmean(pssr(:,ib(1,:)),2) nanmean(pssr(:,ib(1,:)),2)];

for a = 1:4
    p0f(1,a) = wjn_pt(fast_block(:,a));
    p0s(1,a) = wjn_pt(slow_block(:,a));
    psf(1,a) = ttestp(fast_block(:,a),slow_block(:,a),0.05,'right');
end
  


subplot(1,3,3)
b1=mybar(fast_block,col_fast,[1:4]-.1,.25);
hold on 
b2=mybar(slow_block,col_slow,[1:4]+.1,.25);
xlim([.5 4.5])
set(gca,'XTickLabels',{'1st 1/2','2nd 1/2','1st 1/2','2nd half'})
xlabel('Stimulation block         Recovery block')
ylabel('\Delta Speed [%]')
sigbracket('p=0.04',2,18,9)
sigbracket('p=0.01',4,24,9)
sigbracket('p=0.01',3,24,9)
ylim([-30 30])
legend([b1(1) b2(1)],{'Fast','Slow'},'Location','NorthEastOutside')

title({['N = ' num2str(size(fast_block,1)) ' sessions from 6 PD patients'],'Movement velocity adapted DBS'})

figone(7,40)
myprint('perc_one_session_per_patient')
%% Off sessions only
clear all, close all
load peak_velocities_raw.mat
ipat = [1 2 3  7 9 ];%12 14 15];
cmap = wjn_erc_colormap
col_fast = [0.4940, 0.1840, 0.5560];
col_slow = [0.4660, 0.6740, 0.1880];

nr=5;
sk=5;
nn=1:5;
sfs=[];sfr=[];sss=[];ssr=[];asfs=[];asfr=[];asss=[];assr=[];psfs=[];psfr=[];psss=[];pssr=[];
fast_trials_stim = squeeze(peaks_all_raw(nr+1:96-nr,2,ipat));
slow_trials_stim = squeeze(peaks_all_raw(nr+1:96-nr,1,ipat));
fast_trials_rec = squeeze(peaks_all_raw(nr+97:192-nr,2,ipat));
slow_trials_rec = squeeze(peaks_all_raw(nr+97:192-nr,1,ipat));
for a = 1:length(ipat)
    sfs(a,:) = smooth(fast_trials_stim(:,a),sk);
    sss(a,:) = smooth(slow_trials_stim(:,a),sk);
    sfr(a,:) = smooth(fast_trials_rec(:,a),sk);  
    ssr(a,:) = smooth(slow_trials_rec(:,a),sk); 
    
   
    asfs(a,:) = sfs(a,:)-nanmean(sfs(a,nn));
    asfr(a,:) = sfr(a,:)-nanmean(sfs(a,nn));
    asss(a,:) = sss(a,:)-nanmean(sss(a,nn));
    assr(a,:) = ssr(a,:)-nanmean(sss(a,nn));
    
        
    psfs(a,:) = (sfs(a,:)-nanmean(sfs(a,nn)))./nanmean(sfs(a,nn)).*100;
    psfr(a,:) = (sfr(a,:)-nanmean(sfs(a,nn)))./nanmean(sfs(a,nn)).*100;
    psss(a,:) = (sss(a,:)-nanmean(sss(a,nn)))./nanmean(sss(a,nn)).*100;
    pssr(a,:) = (ssr(a,:)-nanmean(sss(a,nn)))./nanmean(ssr(a,nn)).*100;
end

for a = 1:size(sfs,2)
    astim(a) = wjn_ppt(asfs(:,a),asss(:,a));
    arec(a) = wjn_ppt(asfr(:,a),assr(:,a));
    pstim(a) = wjn_ppt(psfs(:,a),psss(:,a));
    prec(a) = wjn_ppt(psfr(:,a),pssr(:,a));
end

ts = 1:size(sfs,2);
tr = size(sfs,2)+1:size(sfs,2)+size(sfr,2);

figure
subplot(1,3,1)
mypower(ts,asfs,col_fast,'sem')
ylim([-1700 1700]/2)
hold on
mypower(ts,asss,col_slow,'sem')
%sigbar(ts,astim<=0.05)
mypower(ts,asfs,col_fast,'sem')
hold on
mypower(ts,asss,col_slow,'sem')
title('Stimulation')
box off
ylabel('Movement velocity [p/s]')
xlabel('Trial')

subplot(1,3,2)
mypower(tr,asfr,col_fast,'sem')
hold on
ylim([-1700 1700]/2)
mypower(tr,assr,col_slow,'sem')
%sigbar(tr,arec<=0.05)
mypower(tr,asfr,col_fast,'sem')
hold on
mypower(tr,assr,col_slow,'sem')
title('Recovery')
box off
set(gca,'YTick',[])
xlabel('Trial')
figone(7,20)


ib = [1:size(assr,2)./2 ;1+size(assr,2)./2:size(assr,2)];
fast_block = [nanmean(asfs(:,ib(1,:)),2) nanmean(asfs(:,ib(2,:)),2) nanmean(asfr(:,ib(1,:)),2) nanmean(asfr(:,ib(1,:)),2)];
slow_block = [nanmean(asss(:,ib(1,:)),2) nanmean(asss(:,ib(2,:)),2) nanmean(assr(:,ib(1,:)),2) nanmean(assr(:,ib(1,:)),2)];

for a = 1:4
    p0f(1,a) = wjn_pt(fast_block(:,a));
    p0s(1,a) = wjn_pt(slow_block(:,a));

    spsf(1,a) = signrank(fast_block(:,a),slow_block(:,a),'tail','right');
    tpsf(1,a) = ttestp(fast_block(:,a),slow_block(:,a),0.05,'right');
end
  


subplot(1,3,3)
b1=mybar(fast_block,col_fast,[1:4]-.1,.25);
hold on 
b2=mybar(slow_block,col_slow,[1:4]+.1,.25);
xlim([.5 4.5])
set(gca,'XTickLabels',{'1st 1/2','2nd 1/2','1st 1/2','2nd half'})
xlabel('Stimulation block   Recovery block')
ylabel('Velocity [p/s]')
sigbracket('p=0.03',1,1450,9)
sigbracket('p=0.006',2,1450,9)
sigbracket('p=0.007',3,1450,9)
sigbracket('p=0.007',4,1450,9)
ylim([-1900 1900]/2)
legend([b1(1) b2(1)],{'Fast','Slow'},'Location','NorthEastOutside')
title({['N = ' num2str(size(fast_block,1)) ' OFF sessions from 5 PD patients'],'Movement velocity adapted DBS'})

figone(7,40)
myprint('OFF_sessions_only_T-Tests')
