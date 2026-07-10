<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reed Bambrough | My Portfolio</title>
    <style>
        :root {
            --bg-color: #0d1117;
            --text-color: #c9d1d9;
            --accent-color: #58a6ff;
            --card-bg: #161b22;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        header {
            margin-bottom: 40px;
            border-bottom: 1px solid #30363d;
            padding-bottom: 20px;
        }
        h1 { color: #ffffff; margin-bottom: 5px; }
        h2 { color: var(--accent-color); margin-top: 30px; }
        .subtitle { color: #8b949e; font-style: italic; margin-top: 0; }
        .card {
            background-color: var(--card-bg);
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .card h3 { margin-top: 0; color: #ffffff; }
        .tag {
            background-color: #1f6feb;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .btn {
            display: inline-block;
            background-color: #21262d;
            color: var(--accent-color);
            padding: 8px 16px;
            border: 1px solid #30363d;
            border-radius: 6px;
            text-decoration: none;
            font-size: 14px;
            margin-top: 10px;
        }
        .btn:hover { background-color: #30363d; }
        ul { padding-left: 20px; }
        li { margin-bottom: 10px; }
    </style>
</head>
<body>

    <div class="container">
        <header>
            <h1>Reed Bambrough</h1>
            <p class="subtitle">9th Grader | Exploring neuroscience, topology, string theory gas cosmology, and mathematical philoosophy</p>
        </header>

        <section id="about">
            <h2>About Me</h2>
            <p>Hello! I am Reed Bambrough, a student going into 9th grade with a heavy passion for neuroscience, theoretical physics, emergent systems, governance, and mathematical philosphy</p>
        </section>

        <section id="projects">
            <h2>Technical Projects</h2>
            <div class="card">
                <h3>NASA NEO Dashboard <span class="tag">Python</span></h3>
                <p>A astrophysics dashboard mockup originally designed as a submission for the stardance competition. It uses NEO data from the NASA JPL Small-Body Database to visualize NEO's trajectories and characteristics on a 2D Plane. Try it out for yourself at the github repo below</p>
                <a href="https://github.com/realreed/NASA-Dashboard-Project" class="btn" target="_blank">View Code on GitHub</a>
            </div>
        </section>

        <section id="essays">
            <h2>Theoretical Notes & Essays</h2>
            <div class="card">
                <h3>Planetary Life Bias & Emergent Behavior</h3>
                <p><em>Abstract:</em> An analysis of the weak anthropic principle in the context of emergent biases in planetary life. Humans are always talking about how current aspects of earth are perfectly "fine-tuned" for life, but this is a bias. Because we are alive, and the planet seems perfect to us, we fail to recognize the fact that the only reason we think it is perfect is because we exist on this planet.</p>
                <p style="color: #8b949e; font-size: 14px;">[Full text coming soon]</p>
            </div>

            <div class="card">
                <h3>The Biobased Anthropic Theory of Emergent Mathematics</h3>
                <p><em>Abstract:</em> An analysis exploring the systenuc relationship between the basis of biological lifeforms, size of the lifeform, state of the lifeform, and general biology of it. This is a direct counter-arguement to Platonism. This mathematical philosphy states that mathematics are emergent principles that arises from the biology of the lifeform thinking of it. For example, a macroscopic, classical physics entity like a human has a biologically coded in understanding of basic arithmetic. Scaling down to planckian scales, a quantum lifeform would have a inherent understanding of mathematical concepts such as quantum dynamics, probability, and uncertainty. Arithmetic, however, would be at the forefront of their scholars knowledge. We also can see how mathematics are simply maps of logic designed to make a chaotic, quantum reality into a neat, logical one for the ease of understanding. We can see how math fails and physics is right in the pauli exclusion principle. In mathematical idealization, two points or objects can occupy the same coordinates or geometric space as another. However, physics pushes back at this in real life. According to the Pauli Exclusion Principle, two identical fermions, like two electrons, cannot have the same exact quantum values. </p>
                <p style="color: #8b949e; font-size: 14px;">[Full text coming soon]</p>
            </div>
        </section>

        <section id="certifications">
            <h2>Certifications & Studies</h2>
            <ul>
                <li><strong>HarvardX: Fundamentals of Neuroscience</strong> — <em>In Progress</em></li>
                <li><strong>Google AI Essentials</strong> — <em>In Progress</em></li>
                <li><strong>GitHub Foundations</strong> — <em>In Progress</em></li>
            </ul>
        </section>
    </div>

</body>
</html>
