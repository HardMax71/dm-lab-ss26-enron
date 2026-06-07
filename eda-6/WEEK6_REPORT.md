<p>This page reports the tasks and outcomes of week 6.</p>

<h3 data-nh-numbering="1.1.1. ">Predicting the person and the group from the mail body</h3>

<p>Last week split the 149 owners into three behavioural groups from how they use mail: 8 broadcasters/executives, 50 outward-facing people, and an internal majority of 85. The text of their messages played no part in that split. This week we ask two things of the body text alone: can it recover the group, and can it name the person who wrote a message. The answers go opposite ways.</p>

<h4 data-nh-numbering="1.1.1.1. ">Tasks of this week</h4>

<p>Prediction experiments, plot creation - Max</p>

<p>Writing of report, creation of presentation, presentation - Len</p>

<h4 data-nh-numbering="1.1.1.2. ">Results/Findings/Outcomes</h4>

<p><strong>Setup.</strong> We pool every cleaned, non-boilerplate body from a profiled author, cap it at 120 per person, and represent the 15,587 messages three ways:</p>

<ul>
<li><strong>TF-IDF words</strong> - a sparse word-count vector, the usual content baseline.</li>
<li><strong>Dense embedding</strong> - the same vocabulary squeezed into 200 latent dimensions.</li>
<li><strong>Char 3-4-grams</strong> - letter patterns that catch spelling and style rather than topic.</li>
</ul>

<p>A linear classifier reads each one.</p>

<p><strong>The group hides from the body.</strong> One catch decides this experiment. Split the messages at random and the same person sits in both train and test, so the model can spot the author and look up their group. Holding out whole people removes that shortcut. The table compares the two splits against a baseline that always guesses "internal", correct on 64% of messages.</p>

<table>
<thead><tr><th>Group prediction (3 classes)</th><th>Random split</th><th>Held-out people</th></tr></thead>
<tbody>
<tr><td>TF-IDF words</td><td>74%</td><td>59%</td></tr>
<tr><td>Dense embedding</td><td>69%</td><td>59%</td></tr>
<tr><td>Char 3-4-grams</td><td>73%</td><td>60%</td></tr>
<tr><td><em>Baseline (always "internal")</em></td><td colspan="2"><em>64%</em></td></tr>
</tbody>
</table>

<p>On a random split every representation beats the baseline. Held out by person, all three fall under it. The confusion matrix shows what happens: for an author it has never read, the model files the broadcasters (under 1 in 20 caught) and most of the outward-facing group into the internal majority.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-6/plots/w6_1_group_prediction.png" alt="Group prediction beats the baseline on a random split but falls below it on held-out people" style="max-width:100%; height:auto;" /></p>

<p><strong>The person does not.</strong> The same vectors name the author with ease. We hold out a fifth of each person's mail and grow the lineup from 10 candidates to 50.</p>

<table>
<thead><tr><th>Author identification (top-1)</th><th>10 people</th><th>30 people</th><th>50 people</th></tr></thead>
<tbody>
<tr><td>TF-IDF words</td><td>74%</td><td>60%</td><td>58%</td></tr>
<tr><td>Char 3-4-grams</td><td>73%</td><td>61%</td><td>60%</td></tr>
<tr><td>Dense embedding</td><td>70%</td><td>53%</td><td>51%</td></tr>
<tr><td><em>Chance</em></td><td><em>10%</em></td><td><em>3%</em></td><td><em>2%</em></td></tr>
</tbody>
</table>

<p>Character style alone nearly matches the full vocabulary. The 200-dimension embedding lags because it drops the rare words that pin a person down. The right panel ranks the 30 most active people by how often their own mail comes back: narrow-topic specialists on top, writers of short internal notes at the bottom.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-6/plots/w6_2_person_identification.png" alt="Author identification sits far above chance for all three representations" style="max-width:100%; height:auto;" /></p>

<p><strong>What the body does carry.</strong> We average each person's message embeddings and project to two dimensions, mapping the corpus by content. The behavioural colours mix together. What sorts the map is topic and desk: the California and power names in one area, trading and contracts in others. The outward-facing group leans to one side, the weak lean the classifier half-caught, but nowhere near a clean split.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-6/plots/w6_3_content_map.png" alt="People mapped by writing content, with the behavioural groups overlapping" style="max-width:100%; height:auto;" /></p>

<p><strong>Individual fingerprints.</strong> Each person's most over-represented words (log-odds with a shrinkage prior, own name removed) read as a clear beat:</p>

<ul>
<li>Kaminski - research, risk, Rice</li>
<li>Dasovich - California, power, electricity</li>
<li>Jones - counterparties, ISDA masters</li>
<li>Arnold - NYMEX, volatility</li>
<li>Forney - ERCOT, the real-time desk</li>
<li>Lokay - pipeline capacity, Transwestern, Waha</li>
</ul>

<p>This is what the author-identification picked up, and what a group label built from reach and broadcast never lines up with.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-6/plots/w6_4_distinctive_words.png" alt="Each person's most distinctive words, a topic signature per individual" style="max-width:100%; height:auto;" /></p>

<h4 data-nh-numbering="1.1.1.3. ">Discussion/Challenges/Special remarks</h4>

<ul>
<li>Who wrote a message is easy to read off the body; which behavioural group they sit in is not. The strong random-split number was author memorisation, not group learning.</li>
<li>The evaluation was the real work. Only a person-level split exposes the leak, and it drops the score by 15 points.</li>
<li>Caveats carry over: the 120-message cap discards volume from the heaviest senders, and two executive desks resolve to an assistant, so "wrote" means "sent from that desk".</li>
</ul>

<h4 data-nh-numbering="1.1.1.4. ">Open Ends</h4>

<p>A sentence-transformer embedding is the obvious next try. But a 200-dimension embedding and character style both already fail the group task while nailing the individual one, so the limit looks like the signal and not the encoder: topic and writing habits belong to the person, the role does not. The next question is whether the group becomes predictable only once the text is joined with the behavioural features it was built from.</p>
