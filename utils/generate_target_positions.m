%% Other operations

% Compute the order of the trials such that each movement occurs in
% pseudo randomized order
 addpath(genpath("utils\"));
target_order = {};
j = 0;
while j < 12
    moves = allcomb([1 2 3 4],[10 20 30 40]); % Compute all possible movements
    moves_all = [];
    for ji = 1:size(moves,1)
        moves_all = [moves_all;unique(perms(moves(ji,:)),'rows')];
    end
    moves_ordered = zeros(length(moves_all), 2);
    for i=1:32
        if i == 1 && length(target_order)==0 % For the first trial choose a random movement
            rest_moves = moves_all;
        elseif i == 1 % choose a movement that continues with the last of the last block
            old_pos = moves_ordered_old(end, 2);
            rest_moves = moves_all(moves_all(:, 1) == old_pos,:);
        else % For later moves chose the moves that start with the same position as the last one
            old_pos = moves_ordered(i-1, 2); % Last positions
            rest_moves = moves_all(moves_all(:, 1) == old_pos,:); % All possible movements
        end
        % Get a random move from the remaining movements
        try
            move = rest_moves(randi(size(rest_moves, 1)), :);
            moves_ordered(i, :) = move;
            moves_all(ismember(moves_all,move,'rows'),:) = []; % Delete chosen move from array
        catch
            disp("no moves left");
        end
    end
    if sum(moves_ordered == 0, [1 2]) == 0
        j = j+1; 
        target_order(j) = {moves_ordered};
        moves_ordered_old = moves_ordered;
    end
end

%% Save the target positions in a form that they can be used in the experiment
% Generate the indexes for two block sets (Periods without a break)
% Every movement 32 times in one block, 6 blocks per block set
i_start = [1,7];
target_pos_y_ind = [];
for j=1:2
    target_pos_block = [];
    for i=i_start(j):i_start(j)+5
        % Get the unique target position (from 1-4)
        tmp = target_order{1, i};
        tmp(tmp==10)=1;  tmp(tmp==20)=2;  tmp(tmp==30)=3;  tmp(tmp==40)=4; 
        if ismember(i,i_start)
            tmp = [tmp(1,1); tmp(:,2)];
        else
           tmp =  tmp(:,2);
        end
        target_pos_block = cat(1,target_pos_block,tmp);
    end
    target_pos_y_ind = cat(2,target_pos_y_ind,target_pos_block);
end
% Save the generated target position
save(strcat(pwd,"/target_pos_y_ind_new.mat"), "target_pos_y_ind");

