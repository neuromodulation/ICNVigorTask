
%% Movement velocity reinforcement task for parkinson patients with DBS

% Slow or fast movements are stimulated
% based on the velocity of the last two movements 
% Task optimized for 3840x2160 screen resolution

% Author: Alessia Cavallo (alessia.cavallo16@gmail.com)

%% Prepare the environment

addpath(genpath("C:\CODE\wjn_toolbox"));
addpath(genpath("C:\CODE\Neuro Omega System SDK"));
addpath(genpath("C:\CODE\Psychtoolbox\PsychInitialize"));
PsychStartup;

clear all; try AO_CloseConnection(); end
time = tic; % Timer from the beginning of the experiment

% Parameter for using the stimulation and neurophysiological recordings
% Only set to false for debugging
use_stim = false;
use_tmsi = false;

% Get input from experimenter
test = ~input("Mode: Write 0=Test or 1=Experiment\n");
modes = ["Experiment","Test"];
disp(strcat("OK, running the ", modes(test+1)));

% If running the test use some default parameters
if test
    stim_amp_R = input("Stimulation amplitude Right:\n");
    stim_amp_L = input("Stimulation amplitude Left:\n");
% For the experiment get more information 
else
    n_par = input("Participant number (Integer):\n");
    % Compute condition based on participant number (alternating order)
    cond = logical(mod(n_par,2));
    conditions = ["Fast-Slow","Slow-Fast"];
    % Ask if other condition is wanted (in case of testing diferent orders
    % with one participant)
    cond_change = input(sprintf(strcat("Condition given by participant number %i: %i (0=Fast/Slow, 1=Slow/Fast). \n",...
                                "Do you want the other condition? (Write 0=No, 1=Yes)\n"),n_par, cond)); 
    if cond_change == 1
        cond = abs(cond-1);
        disp("Condition changed \n");
    else
        disp("Condition not changed \n");
    end
    stim_amp_R = input("Stimulation amplitude Right:\n");
    stim_amp_L = input("Stimulation amplitude Left:\n");
    med = input("Medication: Write 0='MedOff' or 1='MedOn'\n");
    med_options = ["MedOff","MedOn"];
    med = med_options(med+1);
    hand = input("Hand used: Write 0='R' or 1='L'\n");
    hand_options = ["R","L"];
    hand = hand_options(hand+1);
    run = input("Run number: Write number of run starting from 1\n");
end

%% Initialize stimulation settings
if use_stim
    % init neuroomega and display available channels
    availableChannelsID = init_NO();
    display(availableChannelsID);

    % set stimulation parameters !!!!!!!!!!!!!!!!!!!!
    options.stim_channels = [10016, 10017];
    options.stim_return_channel=-1;
    options.stim_amp_R=stim_amp_R; % mA
    options.stim_amp_L=stim_amp_L; % mA
    options.stim_duration = 0.3; % sec
    options.stim_hz=130; % Hz
    options.stim_pw=60; % µs
end

%% Initialize tmsi
if use_tmsi 
     library = TMSi.Library('usb');
    while numel(library.devices) == 0
        library.refreshDevices();
        pause(1);
    end
    device = library.getFirstDevice();
    tmsi_sampler = device.createSampler();
    tmsi_sampler.connect();
    tmsi_sampler.start();
end

%% Initialize Psychtoolbox
Screen('Preference', 'SkipSyncTests', 1);
PsychDefaultSetup(2);
screens = Screen('Screens');
screenNumber = max(screens); % Get the number of the external screen if there is one attached
window_dim = [];%[100 100 1800 900]; % Define the dimension of the psychtoolbox window
[window, windowRect] = Screen('OpenWindow', screenNumber, [0 0 0], window_dim);  % Open a black window
[screenXpixels, screenYpixels] = Screen('WindowSize', window); % Get the dimension of the window in pixels
[xCenter, yCenter] = RectCenter(windowRect); % Get the center coordinates of the window
Screen('TextSize', window, 60); % Set the font size

%% Initialize parameters for the behavioural task

% Define experimental parameters
if test % For the test only perform 15 trials
    n_trials = 15; % Number of trials in each (experimental) block
    n_blocks = 1 ; % Total number of blocks
else
     n_trials = 33;
    n_blocks = 12 ;
end
stim_blocks = [1:3 7:9]; % Blocks during which stimulation is applied
break_blocks = [1 7]; % Blocks befor which a break is introduced
data = []; % Matrix that will contain all behavioral data aquired during the experiment
data_tmsi = []; % Matrix that will contain all neurophysiological data aquired during the experiment
time = tic; % Timer from the beginning of the experiment
threshold_vel_move_start = 2000; % pixel/sec
threshold_vel_change = 1000; % Maximum allowed change of velocity between trials

% Define target properties
target_w_h = 350; % Width = Height of target rectangle
target_size = [0 0 target_w_h target_w_h];
target_pos_y_all = [-300 -150 150 300]; % Possible target positions on the y-axis
target_pos_x_from_center = xCenter - target_w_h/2; % Distance of the target from the center point
target_col_default = [0 200 200 0]; % Default = blue
target_col_change = [200 200 0]; % Change = Yellow (once the pen is on it)
target_col = target_col_default;
target_stay_time = 0.35; % Time that needs to be spent on target for trial completion
side = 1;

% Define properties of the start button
start_button_width = 1000;
start_button_height = 200;
start_button_size = [0 0 start_button_width start_button_height];
start_button_pos_y = 2*yCenter - start_button_height/2;
start_button_pos_x = xCenter;
% The start button will always be at the same position, therefore it can
% already be created here
start_button = CenterRectOnPointd(start_button_size, start_button_pos_x, start_button_pos_y);
break_time_sec = 30; % Time of forced break before stimulation blocks in seconds
start_button_text_pos_y = start_button_pos_y + 20;
header_text_pos_y = start_button_pos_y - 1500;

% Define often used colors
black = [0 0 0];
white = [255 255 255];
purple = [200 0 200];
background_col_default = black;
background_col_change = [100 100 100];

% Load y target positions (same for each participant)
% Makes sure that every movement occurs once in each block (16 possible
% movements between 4 different positions on the y axis)
load('target_pos_y_ind.mat');
traget_pos_y_ind = target_pos_y_ind;

% Other variables
escapeKey = KbName('ESCAPE');

%% Start the experiment 

for i_block=1:n_blocks
   
    % Take a break between some blocks
    if ismember(i_block, break_blocks)
        
        % Draw a welcome text for the first block
        if i_block == 1
            header_text = strcat('Wilkommen! Vielen Dank, dass Sie sich bereit erklären, bei diesem kleinen Experiment teilzunehmen.',...
            ' Ihre Aufgabe ist es, Ihren Stift von einer Seite des Bildschirms zur anderen Seite zu bewegen.',...
            ' Wenn Sie ein Viereck sehen, bewegen Sie den Stift bitte dort hin und bleiben Sie auf dem Viereck, bis auf der anderen Seite',...
            ' ein neues Viereck erscheint. Dann bewegen Sie den Stift zu dem neuen Viereck.',...
            ' Bitte bewegen Sie sich so schnell wie möglich und berühren Sie durchgängig den Bildschirm mit dem Stift.\n \n',...
            ' Sie haben während des Experiments wieherholt die Möglichkeit Pausen einzulegen und Sie können das Experiment jederzeit abbrechen.');
            DrawFormattedText(window,header_text,'center',header_text_pos_y,white,80,[],[],1.5);
        
        % Force a short break for the other blocks
        else
            for i=1:break_time_sec
                header_text = sprintf('PAUSE \n\n\n\n %i',break_time_sec - i);
                DrawFormattedText(window,header_text,'center',header_text_pos_y+250,white);
                w = WaitSecs(1);
                Screen('Flip', window); 
            end  
            DrawFormattedText(window,header_text,'center',header_text_pos_y+250,white);
        end
        button_text = 'Klicken Sie hier, um fortzufahren';

        % Draw the header, start button with text on the screen
        Screen('FillRect', window, white, start_button);
        DrawFormattedText(window,button_text,'center',start_button_text_pos_y,black);
        Screen('Flip', window); 

        % Check if mouse is on button and start the block if this is the case
        block_started = false;
        while ~block_started

            % Exit experiment if escape is pressed
            [keysDown,secs, keyCode] = KbCheck;
            if keyCode(escapeKey)
                sca; 
               if use_stim
                    AO_CloseConnection();
               end
               if use_tmsi
                    tmsi_sampler.stop();
                    tmsi_sampler.disconnect();
                    library.destroy();
               end
            end

            [x_mouse, y_mouse, ~] = GetMouse(window);
            on_start_button = abs(x_mouse - start_button_pos_x) < start_button_width /2 & ...
                abs(y_mouse - start_button_pos_y) < start_button_height /2;
            if on_start_button
                button_text = 'Es geht weiter...';
                Screen('FillRect', window, purple, start_button); % Button turns purple
                DrawFormattedText(window,button_text,'center',start_button_text_pos_y,white);
                Screen('Flip', window); 
                block_started = true;
            end
        end
        wakeup=WaitSecs(0.75); % Wait for 750 ms before start of a block
    
        % Before the start of a period without breaks initalize an array
        % that stores the peak values (used for classification of
        % slow/fast)
        peaks = [];
    end
    
    %% Start a block of n_trials
    for i_trial=1:n_trials
        
        % At the start of each trial...
        side = side * -1; % Change the side the target is displayed
        % Reset the variables
        i_sample = 0; move_started = false; first_sample_after_threshold = true; stim=false;
        % Set the colors back to default
        target_col = target_col_default;
        background_col = background_col_default;
        
        % Get the position of the target and define it
        target_pos_y = yCenter + target_pos_y_all(target_pos_y_ind(i_block, i_trial));
        target_pos_x = xCenter + side * target_pos_x_from_center;
        target = CenterRectOnPointd(target_size, target_pos_x, target_pos_y);
        
        trial_completed = false;
        
        while ~trial_completed
            
            % Draw the traget on the screen 
            Screen('FillRect',window,background_col);
            Screen('FillRect', window, target_col, target);
            Screen('Flip', window); 
            
            % Get the next sample from the mouse 
            [x_mouse, y_mouse, ~] = GetMouse(window);
            sample_time = toc(time);
            global_time = clock;
            global_time = global_time(4:end);
            i_sample = i_sample + 1;
            
            % Get the tmsi samples 
            if use_tmsi 
                samples_tmsi = tmsi_sampler.sample();
            end
        
            % Exit experiment if escape is pressed
            [keysDown,secs, keyCode] = KbCheck;
            if keyCode(escapeKey)
                sca;
                if use_stim
                    AO_CloseConnection();
                end
                if use_tmsi
                    tmsi_sampler.stop();
                    tmsi_sampler.disconnect();
                    library.destroy();
                end
            end
            
            %% Is the target already reached?
            
            % Check if target is reached (mouse is on target rectangle for
            % a specific amount of time)
            on_target = abs(x_mouse - target_pos_x) < target_w_h /2 & ...
                      abs(y_mouse - target_pos_y) < target_w_h /2;
                  
            % If mouse is not on target "delete" the timer and set color of
            % target back to normal
            if ~on_target        
                started_timer = false;
                target_col = target_col_default;
                
            % When mouse is on target for the first time start the timer 
            % and change the target color
            elseif on_target && ~started_timer 
                target_col = target_col_change;
                on_target_time = toc(time); % Timer from first time on target
                started_timer = true;
                
            % If mouse is on target for a specific amount of time set
            % trial_completed to true
            elseif on_target && started_timer
                if toc(time) - on_target_time >= target_stay_time
                    trial_completed = true; 
                end
            end
            
            %% Compute velocity and save the data
                
            % For the first sample save only the positions
            if i_sample == 1 
                x_vel=0;y_vel=0;vel=0;mean_vel=0;
            end

            % If at least 2 samples are taken compute the velocity
            if i_sample >= 2 
                passed_time = sample_time - data(end, 3); % Compute the time passed between the samples
                x_vel = abs(x_mouse - data(end,1)) / passed_time;
                y_vel = abs(y_mouse - data(end,2)) / passed_time;
                vel = sqrt(x_vel.^2 + y_vel.^2); % Velocity independent of direction
                mean_vel = 0;
            end
            % If at least 7 samples are taken compute the average velocity
            if i_sample >= 7
                mean_vel = mean([vel; data(end-5:end,5)], [1, 2]);
            end
            % Save the behavioral data 
            data = cat(1,data,[x_mouse y_mouse sample_time mean_vel vel x_vel y_vel...
                          i_block i_trial on_target stim target_pos_x target_pos_y global_time]);
          
            % Save the neurophysiological data from tmsi 
            if use_tmsi
                data_tmsi = cat(1,data_tmsi,samples_tmsi)
            end
            
            % Set the time of the start of the movement
            if mean_vel > threshold_vel_move_start && ~move_started
                move_start_time = toc(time);
                move_started = true;
            end
            
            %% Stimulation
            % Get the peak of the movement in order to trigger stimulation
            % if...
            % the trial is during a stimulation block or the test
            % the move has started
            % the mean velocity decreased during the last 4 samples --> the
            % peak is passed
            % it is the first time for each movement these conditions are
            % met --> trigger stimulation only once per movement
            if (ismember(i_block, stim_blocks) || test) && move_started && first_sample_after_threshold ...
                && all(diff(data(end-3:end,4)) < 0)
                
                % Get the peak velocity and append it to the array storing
                % all peaks in one set of blocks (without break)
                peak = max(data(end-i_sample:end,4));
                peaks = cat(1, peaks, peak);
                
                % Trigger the stimulation if.. 
                % already 3 movements were performed
                % none of the last 3 movements was an outlier (change
                % between velocities below threshold)
                if length(peaks) > 3 &&  all(abs(diff(data(end-2:end,4))) < threshold_vel_change)
                    peak_diff = peaks(end) - peaks(end-2:end-1);
                    
                    % Trigger the stimulation if..
                    % Slow = Peak velocity lower than the last two movements
                    % Fast = Peak velocity higher than the last two movements
                    % cond = 1 Slow/Fast cond = 0 Fast/Slow
                    % the test is performed
                    if test || all(peak_diff < 0) && cond && ismember(i_block,stim_blocks(1:3)) ||...
                    all(peak_diff < 0) && ~cond && ismember(i_block,stim_blocks(4:6)) ||...
                    all(peak_diff > 0) && ~cond && ismember(i_block,stim_blocks(1:3)) ||...
                    all(peak_diff > 0) && cond && ismember(i_block,stim_blocks(4:6))
                         stim = true;
                         if use_stim
                         %% Send the stimulation trigger to the AO System
                            % Which one is right or left??
                            stimStandard_NO(options.stim_channels(1), options.stim_return_channel, options.stim_amp_R, options.stim_pw, options.stim_hz, options.stim_duration)
                            stimStandard_NO(options.stim_channels(2), options.stim_return_channel, options.stim_amp_L, options.stim_pw, options.stim_hz, options.stim_duration)
                         else % If debugging without AO, use background change to show stimulation
                            background_col = background_col_change; 
                         end
                    end
                end
                first_sample_after_threshold = false;
            end
        end
        Screen('FillRect',window,black);
        Screen('Flip', window);
    end
end
%% Close screen at the end of the experiment and close connections
sca;
if use_stim
    AO_CloseConnection();
end
if use_tmsi
    tmsi_sampler.stop();
    tmsi_sampler.disconnect();
    library.destroy();
end

%% Save the behavioural data for the experimental session
if ~test
    % Generate the BIDS compatible file name 
    if n_par < 10
        n_par = sprintf("0%i",n_par);
    end
    file_name = strcat("sub-",string(n_par),"-",med,"-task-VigorStim-",hand,...
                "-", conditions(cond+1),"-StimOn","-run-0",string(run),...
                "-behavioral.mat");
    % Put all the data into one structure
    options.cond = cond; options.date = date; options.med = med; options.hand = hand; options.run = run;
    options.threshold_vel_move_start = threshold_vel_move_start;
    struct.options = options;
    struct.data = data;
    save(strcat(pwd,'/Data/Parkinson/',file_name), "struct");
    
    % Save the neurophsyiological data
    if use_tmsi
    end
end