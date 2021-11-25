%% Other operations

% Compute the order of the trials such that in two blocks (with 16 trials
% each), each movement occurs once but the order of the movements is
% randomized between pairs of two blocks
target_order = {};
j = 0;
while j < 18
    moves = allcomb([1 2 3 4],[10 20 30 40]); % Compute all possible movements
    moves_all = [];
    for ji = 1:size(moves,1)
        moves_all = [moves_all;unique(perms(moves(ji,:)),'rows')];
    end
    moves_ordered = zeros(length(moves_all), 2);
    for i=1:32
        if i == 1 % For the first trial choose a random movement
            i_move = randi(length(moves_all));
            moves_ordered(i, :) = moves_all(i_move, :);
            moves_all(i_move, :) = []; % Delete chosen move from array
        else % For later moves chose the moves that start with the same position as the last one
            old_pos = moves_ordered(i-1, 2); % Last positions
            rest_moves = moves_all(moves_all(:, 1) == old_pos,:); % All possible movements
            try
                move = rest_moves(randi(size(rest_moves, 1)), :);
                moves_ordered(i, :) = move;
                moves_all(ismember(moves_all,move,'rows'),:) = []; % Delete chosen move from array
            catch
                disp("no moves left");
            end
        end
    end
    if sum(moves_ordered == 0, [1 2]) == 0
        j = j+1; 
        target_order(j) = {moves_ordered};
    end
end

%% Save the target positions in a form that they can be used in the
% experiment 
% Replace the numbers with a 0 (right side) with a single number
target_pos_y_ind = zeros(12,33);
for i=1:18
    tmp = target_order{1, i};
    tmp(tmp==10)=1;  tmp(tmp==20)=2;  tmp(tmp==30)=3;  tmp(tmp==40)=4; 
    target_pos_block = [tmp(1,1); tmp(:,2)]';
    target_pos_y_ind(i,:) = target_pos_block;
end

save(strcat(pwd,"/target_pos_y_ind.mat"), "target_pos_y_ind");
%%

load_tmsi();

