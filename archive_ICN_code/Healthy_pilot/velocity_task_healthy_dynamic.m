
%% Movement velocity task - with dynamic stimulation criteria

% Version: Healthy subjects with visual stimulaton and EEG recording

% Summary: 
% Author: Alessia Cavallo (alessia.cavallo16@gmail.com)

%% Initialize Psychtoolbox
clear all;
PsychDefaultSetup(2);
screens = Screen('Screens');
screenNumber = max(screens); % Get the number of the external screen if there is one attached
window_dim = [];%[100 100 1800 900]; % Define the dimension of the psychtoolbox window
[window, windowRect] = Screen('OpenWindow', screenNumber, [0 0 0], window_dim);  % Open a black window
[screenXpixels, screenYpixels] = Screen('WindowSize', window); % Get the dimension of the window in pixels
[xCenter, yCenter] = RectCenter(windowRect); % Get the center coordinates of the window
Screen('TextSize', window, 30); % Set the font size

%% Initialize parameters

% CHANGE THIS PARAMETERS before start of the experiment
n_par = 1; % Participant number

% Define experimental parameters
slow_first = logical(mod(n_par,2)); % true for odd participant number, false for even ones
stim_blocks = [5 6 9 10]; % Stimulation blocks
no_stim_blocks = [1:4 7 8 11 12]; % Recovery blocks
n_blocks = length([stim_blocks no_stim_blocks]) ; % Total number of blocks
n_trials = 33; % Number of trials in each (experimental) block
data = []; % Matrix that will contain all data aquired during the experiment
stim_time = 0.3; % Duration of stimulation in sec
time = tic; % Timer from the beginning of the experiment

% Define target properties
target_w_h = 150; % Width = Height of target rectangle
target_size = [0 0 target_w_h target_w_h];
target_pos_y_all = [-150 -50 50 150]; % Possible target positions on the y-axis
target_pos_x_from_center = xCenter - target_w_h/2; % Distance of the target from the center point
target_col_default = [0 0 200 200]; % Default = blue
target_col_change = [200 200 0]; % Change = Yellow (once the pen is on it)
target_col = target_col_default;
target_stay_time = 0.35; % Time that needs to be spent on target for trial completion

% Define properties of the start button
start_button_width = 500;
start_button_height = 100;
start_button_size = [0 0 start_button_width start_button_height];
start_button_pos_y = 2*yCenter - start_button_height/2;
start_button_pos_x = xCenter;
% The start button will always be at the same position, therefore it can
% already be created here
start_button = CenterRectOnPointd(start_button_size, start_button_pos_x, start_button_pos_y);
break_time_sec = 30; % Time of forced break before stimulation blocks in seconds
start_button_text_pos_y = start_button_pos_y + 10;
header_text_pos_y = start_button_pos_y - 500;

% Define often used colors
black = [0 0 0];
white = [255 255 255];
purple = [200 0 200];
background_col_default = black;
background_col_change = black ;%[100 100 100];

% Variable that need to be initialized but will be changed
side = 1; threshold_slow = 0; threshold_fast = inf; threshold_time_slow = inf; threshold_time_fast = inf;

% Load y target positions (same for each participant)
% Makes sure that every movement occurs once in each block (16 possible
% movements between 4 different positions on the y axis)
load('target_pos_y_ind.mat');
traget_pos_y_ind = target_pos_y_ind;

% Other variables
escapeKey = KbName('ESCAPE');
background_col = background_col_default;

%% Start the experiment 

for i_block=1:n_blocks
   
    % Force break before stimulation blocks
    if ismember(i_block, stim_blocks([1 3]))
        header_text = strcat('Zeit für eine kleine Pause');
        button_text = 'Klicken Sie hier um fortzufahren';
        for i=1:break_time_sec
            % Draw timer
            counter_text = char('PAUSE  ' + string(break_time_sec-i) );
            DrawFormattedText(window,counter_text,'center',start_button_pos_y,purple);
            % Draw header
            DrawFormattedText(window,header_text,'center',header_text_pos_y,white);
            w = WaitSecs(1);
            Screen('Flip', window); 
        end  
    else % Between blocks (possibility for a break)
        header_text = ''; 
        button_text = 'Klicken Sie hier um fortzufahren';
    end
    
    % Draw the header, start button with text on the screen
    DrawFormattedText(window,header_text,'center',header_text_pos_y,white);
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
    wakeup=WaitSecs(0.75); % Wait for 750 ms before start of the experiment and the next block
    
    % Determine which time threshold should be used 
    if (ismember(i_block, stim_blocks(1:2)) && slow_first) || (ismember(i_block, stim_blocks(3:end)) && ~slow_first)
        threshold_time = threshold_time_slow;
    elseif ismember(i_block,stim_blocks)
        threshold_time = threshold_time_fast;
    end
    
    %% Start the actual trials
    
    for i_trial=1:n_trials
        
        % At the start of each trial...
        side = side * -1; % Change the side the target is displayed
        % Reset the variables
        stim = false; stim_started_time = 0; i_sample = 0; first_sample_after_threshold = true; move_started = false;
        % Set the colors back to default
        target_col = target_col_default;
        background_col = background_col_default;
        % Add 5 lines of zeros to the data for the computation of the mean
        % velocity at the beginning of the trial 
        data = cat(1,data,zeros(5,16)); 
        
        % Get the position of the target
        target_pos_y = yCenter + target_pos_y_all(target_pos_y_ind(i_block, i_trial));
        target_pos_x = xCenter + side * target_pos_x_from_center;
            
        % Draw the target rectangle on that position
        target = CenterRectOnPointd(target_size, target_pos_x, target_pos_y);
        Screen('FillRect', window, target_col, target);
        Screen('Flip', window);
        
        trial_completed = false;
        while ~trial_completed
            
            % Exit experiment if escape is pressed
            [keysDown,secs, keyCode] = KbCheck;
            if keyCode(escapeKey)
                sca; 
            end
            
            % Check if target is reached (mouse is on target rectangle for
            % a specific amount of time)
            [x_mouse, y_mouse, ~] = GetMouse(window);
            sample_time = toc(time);
            global_time = clock;
            global_time = global_time(4:end);
            i_sample = i_sample + 1;
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
            
            % Draw the traget on the screen 
            Screen('FillRect',window,background_col); % Changes the background to a different color in case of stimulation
            Screen('FillRect', window, target_col, target);
            Screen('Flip', window); 
            
            % Compute velocity and save the data
                
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
                % Compute the average over 7 samples
                mean_vel = mean([vel; data(end-5:end,5)], [1, 2]); 
            end
            
            if i_block == 1
                % Save the data (Add 2 to the block number such that the two
                % blocks of the training can be appended at the end)
                data = cat(1,data,[x_mouse y_mouse sample_time mean_vel vel x_vel y_vel...
                              i_block-1 i_trial-1 on_target stim target_pos_x target_pos_y global_time]);
            else
                % Save the data (Add 2 to the block number such that the two
                % blocks of the training can be appended at the end)
                data = cat(1,data,[x_mouse y_mouse sample_time mean_vel vel x_vel y_vel...
                                  i_block+1 i_trial-1 on_target stim target_pos_x target_pos_y global_time...
                                  threshold_slow threshold_fast threshold_time_slow threshold_time_fast]);
            end

            % Set the time of the start of the movement (positive velocity)
            if mean_vel > 100 && ~move_started
                move_start_time = toc(time);
                move_started = true;
            end
            
            % If in a stimulation block, after the time threshold (75 % percentile of peak times)
            % is crossed, check whether the stimulation the conditions for slow/fast
            % stimulation are met
            % Stimulate also in each trial after 0.5 sec in the second familiarization block
            if ismember(i_block, stim_blocks) && i_trial ~= 1 && move_started 
                if sample_time - move_start_time > threshold_time
                    if first_sample_after_threshold
                        % Compute peak velocity for the last samples
                         peak = max(data(end-i_sample:end,4));
                        if (peak < threshold_slow && slow_first && ismember(i_block,stim_blocks(1:2))) ||...
                           (peak > threshold_fast && slow_first && ismember(i_block,stim_blocks(3:end))) ||...
                           (peak < threshold_slow && ~slow_first && ismember(i_block,stim_blocks(3:end))) ||...
                           (peak > threshold_fast && ~slow_first && ismember(i_block,stim_blocks(1:2)))
                            background_col = background_col_change;
                            stim_started_time = toc(time);
                            stim = true;
                        end
                        first_sample_after_threshold = false;
                        % Change back if stimultion time is passed
                    elseif stim
                        if toc(time) - stim_started_time >= stim_time
                            background_col = background_col_default;
                            stim = false;
                        end
                    end
                end
            end
        end
        Screen('FillRect',window,background_col_default); % Make sure that the background color goes back to default at the end of a trial
    
        %% Compute new thresholds
        % Update the threshold every 16 movements (based on the last 16
        % movements)
        if ismember(i_trial,[16 32])
            peak_vels = zeros(16,1);
            peak_times = zeros(16,1);
            for i_t=i_trial-16+1:i_trial
                % Get the data for one block and trial (when the movement
                % has started --> data(:,4) > 100)
                mask = data(:,8) == i_block & data(:,9) == i_t & data(:,4) > 100; 
                data_trial = data(mask, :);
                % Get the peak velocity and its time point in that trial
                % (in respect to the start of the movement)
                [peak, index]  = max(data_trial(:,4));
                peak_vels(i_t) = peak;
                peak_times(i_t) = data_trial(index,3)-data_trial(1,3);
            end
            % Compute the thresholds 
            threshold_slow =  prctile(peak_vels,(100/3),'all');
            threshold_fast =  prctile(peak_vels,(100/3)*2,'all');
            peak_times_slow = peak_times(peak_vels < threshold_slow);
            peak_times_fast = peak_times(peak_vels > threshold_fast);
            threshold_time_slow = prctile(peak_times_slow,85,'all');
            threshold_time_fast = prctile(peak_times_fast,85,'all');
        end
    end
end
sca; % Close screen at the end of the experiment

%% Save the data 
save(strcat(pwd,'/Data/',sprintf("Participant_%i.mat",n_par)), "data");
more_info = [slow_first];
save(strcat(pwd,'/Data/',sprintf("Participant_%i_info.mat",n_par)), "more_info");