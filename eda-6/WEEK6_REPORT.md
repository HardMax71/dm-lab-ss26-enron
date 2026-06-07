<p>This page reports the tasks and outcomes of week 6.</p>
<h3>Leftovers from last week</h3>
<p>
  [Max] Add clustered Person plots to the wiki week 5 - Done, see
  <ac:link
    ><ri:page
      ri:space-key="TUMddmlab"
      ri:content-title="Enron Group_Report Week 5_26" /></ac:link
  ><br />[Max] Do prediction on mail body only, to which of these person groups
  this mail belongs (in 2-3 weeks) (vector or embedding prediction), differences
  between individual persons
</p>
<p>[Len] explain the shift of timing </p>
<p>
  [Both] Reading of other weekly reports, some feedback sentences for the weekly
  reports
</p>
<h4>Tasks of this week</h4>
<p>Plot Creation - Max</p>
<p>Writing of Report, Creation of Presentation, Presentation - Len</p>
<h4>Results/Findings/Outcomes</h4>
<p>
  This week we ask what a message body alone says about its author. Two
  questions: can a model name the behavioural group the author belongs to, and
  can it name the person who wrote the message. The answers go opposite ways, and
  the gap between them is the result.
</p>
<h5>The three behavioural groups</h5>
<p>
  Last week we sorted the mailbox owners into three groups by how they use mail,
  not by what they write about. There are 150 mailbox folders but 149 people: the
  folder <code>phanis-s</code> is a garbled duplicate of <code>panus-s</code>
  (both are Stephanie Panus), so it was merged. For each owner we built twelve
  features - message volume, message length, recipients per message, share of
  mail that leaves the company, share sent to more than five people, how often
  they start a thread, weekend share, months active, mailbox deletion rate, and
  the number of colleagues they write to and hear from. Features that span orders
  of magnitude were log-scaled, all were standardised, and a Ward hierarchical
  clustering was cut where the silhouette score was highest, at three groups. The
  full method and the cluster plots are on the
  <ac:link
    ><ri:page
      ri:space-key="TUMddmlab"
      ri:content-title="Enron Group_Report Week 5_26" /></ac:link
  >.
</p>
<ul>
  <li>
    <strong>Broadcasters / execs (8 people).</strong> The longest messages
    (median 260 characters) sent to the most people at once (about 10 recipients,
    against 2 for everyone else), with the widest reach. This is announcement and
    direction-setting mail.
  </li>
  <li>
    <strong>Outward-facing (50 people).</strong> Most of their mail leaves the
    company (40% external, against about 20%), and their internal footprint is the
    smallest - they write to roughly 9 colleagues, against 22 for the majority.
    These are the deal and counterparty contacts.
  </li>
  <li>
    <strong>Internal majority (85 people).</strong> The most messages (about 1,000
    each on average), the densest internal network, the most Cc traffic, the
    lowest deletion, and the least external mail. These people run the inside of
    the company.
  </li>
</ul>
<h5>Preparing the messages</h5>
<p>
  We take every cleaned, non-boilerplate body from a profiled author. A few people
  send far more than the rest - Dasovich about 4,900 messages, Mann 4,500, then
  Shackleton, Kaminski, Jones and Germany each above 3,000 - so without a limit
  they would dominate both the training data and the author test. We cap each
  person at 120 messages; 112 of the 143 people clear that line, and the cap only
  trims the heaviest senders, leaving 15,587 messages. Each one is turned into
  three representations:
</p>
<ul>
  <li>TF-IDF words - a sparse word-count vector, the usual content baseline.</li>
  <li>
    Dense embedding - the same vocabulary compressed into 200 dimensions (a
    truncated SVD of the word matrix).
  </li>
  <li>
    Char 3-4-grams - short letter patterns that catch spelling and style rather
    than topic.
  </li>
</ul>
<p>A linear classifier reads each one.</p>
<h5>Can the body predict the group?</h5>
<p>
  One catch decides this experiment. If we split the messages at random, the same
  person sits in both the training and the test set, so the model can recognise
  the author and look up their group instead of learning the group from the words.
  Holding out whole people removes that shortcut: every author in the test set is
  one the model never read. The table compares the two splits against a baseline
  that always guesses &quot;internal&quot;, right on 64% of messages.
</p>
<table>
  <thead>
    <tr>
      <th>Group prediction (3 classes)</th>
      <th>Random split</th>
      <th>Held-out people</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>TF-IDF words</td>
      <td>74%</td>
      <td>59%</td>
    </tr>
    <tr>
      <td>Dense embedding</td>
      <td>69%</td>
      <td>59%</td>
    </tr>
    <tr>
      <td>Char 3-4-grams</td>
      <td>73%</td>
      <td>60%</td>
    </tr>
    <tr>
      <td><em>Baseline (always &quot;internal&quot;)</em></td>
      <td colspan="2"><em>64%</em></td>
    </tr>
  </tbody>
</table>
<p>
  On a random split every representation beats the baseline. Held out by person,
  all three fall under it. The confusion matrix on the right shows what happens:
  for an author it has never read, the model puts the broadcasters (under 1 in 20
  caught) and most of the outward-facing group into the internal majority.
</p>
<p>
  <img
    style="max-width: 100.0%;height: auto;"
    src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-6/plots/w6_1_group_prediction.png"
    alt="Group prediction beats the baseline on a random split but falls below it on held-out people"
  />
</p>
<h5>Can the body name the person?</h5>
<p>
  The same vectors name the author with ease. Here the author is meant to appear
  in both sets, so we hold out a fifth of each person's mail and grow the lineup
  from 10 candidates to 50.
</p>
<table>
  <thead>
    <tr>
      <th>Author identification (top-1)</th>
      <th>10 people</th>
      <th>30 people</th>
      <th>50 people</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>TF-IDF words</td>
      <td>74%</td>
      <td>60%</td>
      <td>58%</td>
    </tr>
    <tr>
      <td>Char 3-4-grams</td>
      <td>73%</td>
      <td>61%</td>
      <td>60%</td>
    </tr>
    <tr>
      <td>Dense embedding</td>
      <td>70%</td>
      <td>53%</td>
      <td>51%</td>
    </tr>
    <tr>
      <td><em>Chance</em></td>
      <td><em>10%</em></td>
      <td><em>3%</em></td>
      <td><em>2%</em></td>
    </tr>
  </tbody>
</table>
<p>
  Character style alone nearly matches the full vocabulary. The 200-dimension
  embedding lags because it drops the rare words that pin a person down. The right
  panel ranks the 30 most active people by how often their own mail comes back:
  people with a narrow topic on top, writers of short internal notes at the bottom.
</p>
<p>
  <img
    style="max-width: 100.0%;height: auto;"
    src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-6/plots/w6_2_person_identification.png"
    alt="Author identification sits far above chance for all three representations"
  />
</p>
<h5>What the body actually encodes</h5>
<p>
  If the body names the person but not the group, what does it carry? We average
  each person's message embeddings into one point and project those points to two
  dimensions, mapping the corpus by content. The group colours mix together. What
  sorts the map is topic and desk: the California and power names sit in one area,
  trading and contracts in others. The outward-facing group leans to one side -
  the weak signal the classifier half-caught - but there is no clean split.
</p>
<p>
  <img
    style="max-width: 100.0%;height: auto;"
    src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-6/plots/w6_3_content_map.png"
    alt="People mapped by writing content, with the behavioural groups overlapping"
  />
</p>
<h5>Why each person's words give them away</h5>
<p>
  For nine well-known people we take the words most over-used in their own mail
  against everyone else's (a log-odds score with a shrinkage prior, with their own
  name removed). Reading the actual messages behind those words shows where each
  one comes from.
</p>
<table>
  <thead>
    <tr>
      <th>Person and role</th>
      <th>Top words</th>
      <th>What they point to</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Vince Kaminski - head of the research group</td>
      <td>research, risk, Rice, resume, Shirley</td>
      <td>His group's risk-modelling work, constant hiring (Rice University students, forwarded resumes), and his assistant Shirley Crenshaw.</td>
    </tr>
    <tr>
      <td>Jeff Dasovich - government-relations, California</td>
      <td>California, power, electricity, Davis, PUC</td>
      <td>The 2000-01 California power crisis: Governor Gray Davis, the Public Utilities Commission, electricity prices.</td>
    </tr>
    <tr>
      <td>Tana Jones - senior legal specialist, ENA</td>
      <td>ISDA, master, counterparty, database</td>
      <td>She tracked executed ISDA master agreements ("400 and counting") and ran the trading-agreement database.</td>
    </tr>
    <tr>
      <td>John Arnold - natural-gas trader</td>
      <td>NYMEX, vol, ICE</td>
      <td>Futures and options trading: the NYMEX exchange, volatility, the ICE electronic platform.</td>
    </tr>
    <tr>
      <td>John Forney - real-time power trader, West</td>
      <td>ERCOT, EnPower, balancing, TECO</td>
      <td>Real-time grid dispatch: the Texas ERCOT market, Enron's EnPower scheduling system, balancing bids.</td>
    </tr>
    <tr>
      <td>Sara Shackleton - senior counsel, ENA</td>
      <td>ISDA, Smith Street, North America, fax</td>
      <td>Contract terms plus her own letterhead: 1400 Smith Street (Enron's address), Enron North America, fax cover sheets.</td>
    </tr>
    <tr>
      <td>Sally Beck - managing director, operations</td>
      <td>positions, team, London, Patti, Beth</td>
      <td>Running trade operations across desks and offices, coordinating named team members.</td>
    </tr>
    <tr>
      <td>Michelle Lokay - Transwestern pipeline desk</td>
      <td>MMBtu, Transwestern, Waha, capacity, San Juan</td>
      <td>Gas-pipeline scheduling: the Transwestern line, its Waha and San Juan delivery points, capacity measured in MMBtu.</td>
    </tr>
    <tr>
      <td>Chris Germany - gas trader, East desk</td>
      <td>Dth, Dominion, CNG, compression</td>
      <td>East-region gas deals and pipeline notices: dekatherms, the Dominion and CNG systems, compression and production postings.</td>
    </tr>
  </tbody>
</table>
<p>
  The words split into two kinds: the vocabulary of a desk (NYMEX, ISDA, MMBtu,
  ERCOT) and the local names around a person (an assistant, a pipeline point, an
  office address). Both stay the same over time, so the classifier learns them and
  the person is easy to place. Neither tracks the behavioural group - a broadcaster
  and an internal-majority trader can both write "MMBtu" - which is why the group
  stays invisible in the words.
</p>
<p>
  <img
    style="max-width: 100.0%;height: auto;"
    src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-6/plots/w6_4_distinctive_words.png"
    alt="Each person's most distinctive words, a topic signature per individual"
  />
</p>
<p><strong>Shift of timing - Len</strong></p>
<p>// TODO</p>
<p><br /></p>
<h4>Discussion/Challenges/Special remarks</h4>
<ul>
  <li>
    Who wrote a message is easy to read from the body; which group they belong to
    is not. The strong random-split number was the model recognising the author,
    not learning the group.
  </li>
  <li>
    The evaluation mattered more than the model. Only holding out whole people
    exposes the leak, and it drops group accuracy by 15 points, from 74% to 59%.
  </li>
  <li>
    Caveats carry over: the 120-message cap drops volume from the heaviest senders,
    and two executive desks resolve to an assistant, so &quot;wrote&quot; there
    means &quot;sent from that desk&quot;.
  </li>
</ul>
<h4>Open Ends</h4>
<p>
  The open question was whether the group becomes predictable once the body text
  is joined with the behavioural features the groups were built from. We checked it
  directly: we attached each author's twelve features to every one of their
  messages and predicted the group for held-out people three ways.
</p>
<p>
  <img
    style="max-width: 100.0%;height: auto;"
    src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-6/plots/w6_5_text_plus_behaviour.png"
    alt="Held-out group accuracy from text, behaviour, and both combined"
  />
</p>
<p>
  Text alone stays at 59%, below the baseline. Behaviour alone reaches 87%, and the
  two together 88%. So the group is predictable for an unseen person, but from how
  they communicate, not from what they write - text adds about one point. Since the
  groups were defined from those features, behaviour recovering them is expected;
  the point is that the words contribute almost nothing on top.
</p>
<p>
  A sentence-transformer embedding might lift the text bar a little, but a
  200-dimension embedding and character style both already fail the group task
  while naming the person, so the limit looks like the signal, not the encoder.
  Topic and writing habits belong to the person; the behavioural role does not.
  Predicting that role needs the behavioural signal alongside the text.
</p>
<p><br /></p>
