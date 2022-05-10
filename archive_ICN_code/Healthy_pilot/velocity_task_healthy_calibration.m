
%% Movement velocity task - Calibration

% Version: Healthy subjects with visual stimulaton and EEG recording

% Summary: This script performs the calibration of the velocity task,
% meaning it determines the thresholds for calibraion (of slow and fast
% movements) in the velocity reinforcement task. This calibration is made
% out of six blocks where the first two blocks are very short and merely
% serve as a familiarization. The next two blocks are needed for the
% participant to learn the task. The last two blocks are used to determine
% the stimulation criteria. However, before setting the threshold it is
% checked whether the distributions of the peak velocities of the last two
% blocks are different from each other, specifically if the mean of the last 
% one is higher than the one before. In that case an extra block is needed
% to make sure that the thresholds are based on two blocks with constant
% mean peak velocity. (The computation of the threshold is done in another
% script as I can't manage to plot and run psychtoolbox in one matlab instance :()

% Author: Alessia Cavallo (alessia.cavallo16@gmail.com)

%% Initialize Psychtoolbox
Screen('Preference', 'SkipSyncTests', 1);
PsychDefaultSetup(2);
screens = Screen('Screens');
screenNumber = max(screens); % Get the number of the external screen if there is one attached
window_dim =[];%[100 100 1800 900]; % Define the dimension of the psychtoolbox window
[window, windowRect] = Screen('OpenWindow', screenNumber, [0 0 0], window_dim);  % Open a black window
[screenXpixels, screenYpixels] = Screen('WindowSize', window); % Get the dimension of the window in pixels
[xCenter, yCenter] = RectCenter(windowRect); % Get the center coordinates of the window
Screen('TextSize', window, 60); % Set the font size

%% Initialize parameters

% CHANGE THIS PARAMETERS before start of the experiment
n_par = 9; % Participant number
first_calibration = true; 
%first_calibration = false; % Change to false if extra blocks are needed (the participant has not reached his 
% peak velocity yet)
n_extra_blocks = 2;

% Define experimental parameters
fam_blocks = 1:2; % Familiarization blocks
train_blocks = 3:6; % Training blocks (Only use the last two for threshold detection - calibration blocks)
n_blocks = length([fam_blocks train_blocks]); % Total number of blocks
n_trials = 33; % Number of trials in each (experimental) block
n_trials_block = [10 10 repmat(n_trials,1,8)]; % Number of trials in each block (less for familiarization blocks)
time = tic; % Timer from the beginning of the experiment
stim_time = 0.3; % Duration of stimulation in sec

% If more blocks are needed for calibration change the block numbers
% accoridngly (append data to existing matrix)
if first_calibration
    data = []; % Matrix that will contain all data aquired during the experiment
    i_block_start = 1;
    i_block_end = train_blocks(end);
else
    i_block_start = i_block_end+1;
    i_block_end = i_block_start+n_extra_blocks-1;
end 

% Define target properties
target_w_h = 300; % Width = Height of target rectangle
target_size = [0 0 target_w_h target_w_h];
target_pos_y_all = [-300 -150 150 300]; % Possible target positions on the y-axis
target_pos_x_from_center = xCenter - target_w_h/2; % Distance of the target from the center point
target_col_default = [0 0 200 200]; % Default = blue
target_col_change = [200 200 0]; % Change = Yellow (once the pen is on it)
target_col = target_col_default;
target_stay_time = 0.35; % Time that needs to be spent on target for trial completion

% Define properties of the start button
start_button_width =1000;
start_button_height = 200;
start_button_size = [0 0 start_button_width start_button_height];
start_button_pos_y = 2*yCenter - start_button_height/2;
start_button_pos_x = xCenter;
% The start button will always be at the same position, therefore it can
% already be created here
start_button = CenterRectOnPointd(start_button_size, start_button_pos_x, start_button_pos_y);
break_time_sec = 30; % Time of forced break before stimulation blocks in seconds
start_button_text_pos_y = start_button_pos_y + 20;
header_text_pos_y = start_button_pos_y - 1000;

% Define often used colors
black = [0 0 0];
white = [255 255 255];
purple = [200 0 200];
background_col_default = black;
background_col_change = [100 100 100];

% Variable that need to be initialized but will be changed
threshold_time = 0.3; side = 1;

% Load y target positions (same for each participant)
% Makes sure that every movement occurs once in each block (16 possible
% movements between 4 different positions on the y axis)
load('target_pos_y_ind.mat');

% Other variables
escapeKey = KbName('ESCAPE');
background_col = background_col_default;

%% Start the esxperiment 

for i_block=i_block_start:i_block_end
    
    % Show different text before different blocks
    if i_block == 1 % Before start of the familiarization
        header_text = strcat('Welcome! In this experiment you will see a rectangle on either side of the screen. \n',... 
        'Your task will be to move your pen on the rectangle. When you reach the rectangle its color will change. \n',... 
        'You have to stay on the rectangle until is disappears and the rectangle on the other side appears.\n',... 
        'In a nutshell, you have to move your pen from one rectangle to the other.  \n',... 
        'Try to keep the velocity of your movements as constant as possible meaning that you should not try \n',...
        'to get faster over time but rather to keep the same velocity. Now we will start the familiarization. \n',...
        'This part of the experiment will not be recorded, it is just for you to get to know the task.\n');
        button_text = 'Click here to start';
    elseif i_block == 2 % Before start of the stimulation familiarization 
        header_text = strcat('Sometimes the screen will change color.Try to ignore that as much as possible.\n',...
        'Now you can try the task with this change of background color. \n',...
        'This part will not be recorded. ');
        button_text = 'Click here to start';
    elseif i_block == 3 % Before start of the training
        header_text = 'Are the instructions clear? Then let us start with the experiment';
        button_text = 'Click here to start';
    else % Between blocks
        header_text = 'Break'; 
        button_text = 'Click here to continue';
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
            button_text = 'Get ready...';
            Screen('FillRect', window, purple, start_button); % Button turns purple
            DrawFormattedText(window,button_text,'center',start_button_text_pos_y,white);
            Screen('Flip', window); 
            block_started = true;
        end
    end
    wakeup=WaitSecs(0.75); % Wait for 750 ms before start of the experiment and the next block
    
    %% Start the actual trials
    
    for i_trial=1:n_trials_block(i_block)
        
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

            % Save the data
            data = cat(1,data,[x_mouse y_mouse sample_time mean_vel vel x_vel y_vel...
                              i_block-2 i_trial-1 on_target stim target_pos_x target_pos_y global_time]);

            % Set the time of the start of the movement (positive velocity)
            if mean_vel > 100 && ~move_started
                move_start_time = toc(time);
                move_started = true;
            end
            
            % If in a stimulation block, after the time threshold (75 % percentile of peak times)
            % is crossed, check whether the stimulation the conditions for slow/fast
            % stimulation are met
            % Stimulate also in each trial after 0.5 sec in the second familiarization block
            if i_block == 2 && move_started 
                if sample_time - move_start_time > threshold_time
                    if first_sample_after_threshold
                        % Compute peak velocity for the last samples
                        background_col = background_col_change;
                        stim_started_time = toc(time);
                        stim = true;
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
    end
end
sca; % Close screen at the end of the experiment

%% Save the data 
data_calibration = data;
save(strcat(pwd,'/Data/',sprintf("Calibration_Participant_%i.mat",n_par)), "data_calibration");