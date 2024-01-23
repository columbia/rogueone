#/bin/bash

while true
do
python rogue_one_runner.py --sample_folder /home/rjs2247/workspace/RogueOneSamples/
python gather_data.py /home/rjs2247/workspace/RogueOneSamples/
python changed_file_lists.py /home/rjs2247/workspace/RogueOneSamples/
python rogue_one_runner.py --sample_folder /home/rjs2247/workspace/RogueOneSamples/
python gather_data.py /home/rjs2247/workspace/RogueOneSamples/
done
