import React, { useEffect } from "react";

export default function HelpModal({ open, onClose }) {
  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    // Prevent the page behind from scrolling while the help is open.
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="help-backdrop"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="help-window"
        role="dialog"
        aria-modal="true"
        aria-labelledby="help-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="help-head">
          <h2 id="help-title">Chess Tree Analyzer — User Guide</h2>
          <button
            className="help-close"
            onClick={onClose}
            aria-label="Close help"
            title="Close this guide (Esc)"
          >
            ✕
          </button>
        </div>

        <div className="help-body">
          <p className="help-lead">
            This guide explains everything you need to use the Chess Tree
            Analyzer, even if you have never used it before. Take your time —
            you can leave this window open while you try things out.
          </p>

          <nav className="help-toc">
            <a href="#help-what">What this app does</a>
            <a href="#help-start">Your first analysis in 3 steps</a>
            <a href="#help-input">Choosing a position</a>
            <a href="#help-engine">Choosing your engine</a>
            <a href="#help-settings">Analysis settings</a>
            <a href="#help-board">The board &amp; navigation</a>
            <a href="#help-tree">The variation tree</a>
            <a href="#help-evals">How evaluations are shown</a>
            <a href="#help-export">Saving your results</a>
            <a href="#help-glossary">Glossary</a>
          </nav>

          <section id="help-what">
            <h3>What this app does</h3>
            <p>
              You give the app a chess position. It then uses the Stockfish
              chess engine to look at the best replies, and the best replies to
              those replies, and so on — building a branching “tree” of the most
              important lines. You can click through every branch on the board
              and save the whole thing to a file.
            </p>
            <p>
              <strong>Everything happens on your own computer, inside your web
              browser.</strong> Nothing is uploaded to a server, you don’t need
              an account, and the chess engine runs locally on your machine. The
              first time you open the app it loads the engine — when the dot in
              the top-right corner turns green and says “Engine ready,” you’re
              good to go.
            </p>
          </section>

          <section id="help-start">
            <h3>Your first analysis in 3 steps</h3>
            <ol>
              <li>
                <strong>Pick a position.</strong> The easiest way to start: in
                the <em>Position Input</em> box on the left, keep the{" "}
                <em>PGN Game</em> tab selected and click{" "}
                <em>Load sample game</em>.
              </li>
              <li>
                <strong>Press <em>Generate Tree</em>.</strong> The big green
                button on the left starts the analysis. A progress bar shows how
                many positions have been looked at.
              </li>
              <li>
                <strong>Explore the results.</strong> When it finishes, the
                variation tree appears on the right. Click any move to see that
                position on the board in the middle.
              </li>
            </ol>
            <p className="help-tip">
              Tip: the default settings are a good starting point. Once you’re
              comfortable, raise <em>Max depth</em> for deeper trees — just know
              that deeper trees take longer.
            </p>
          </section>

          <section id="help-input">
            <h3>Choosing a position</h3>
            <p>
              The <em>Position Input</em> card has three tabs. Pick whichever
              suits you:
            </p>
            <h4>PGN Game</h4>
            <p>
              PGN is the standard text format for a recorded chess game. Paste a
              game into the box (for example{" "}
              <code>1. e4 e5 2. Nf3 Nc6 3. Bb5</code>), or click{" "}
              <em>Upload PGN file</em> to load a <code>.pgn</code> file from your
              computer. The moves of the game become the starting line, and the
              app analyses outward from the final position. <em>Load sample
              game</em> fills the box with an example so you can try it
              instantly.
            </p>
            <h4>FEN Position</h4>
            <p>
              FEN is a short code that describes one exact board position. If you
              already have a FEN string, paste it here to analyse that single
              position. Click <em>Use starting position</em> to reset it to the
              normal chess starting setup.
            </p>
            <h4>Play on Board</h4>
            <p>
              Prefer to set things up by hand? Choose this tab and drag the
              pieces on the board to play out the moves you want. Those moves
              become the starting line. Use <em>Undo move</em> to take back the
              last move, or <em>Reset board</em> to start over.
            </p>
          </section>

          <section id="help-engine">
            <h3>Choosing your engine</h3>
            <p>
              The <em>Engine</em> card at the top-left lets you pick which chess
              engine does the thinking. Most people never need to change this.
            </p>
            <h4>Built-in (browser)</h4>
            <p>
              The default. A copy of Stockfish 16 is bundled with the app and
              runs right inside your web browser — nothing to download or set up,
              and it works everywhere, including the published online version.
              The one trade-off is that this in-browser version runs on a single
              CPU core.
            </p>
            <h4>My own engine (local)</h4>
            <p>
              If you have downloaded your own chess engine program to your
              computer (for example a newer Stockfish, or a different engine
              entirely), you can have the app use that instead. This only works
              when you’re running the app on your own machine, and it can use{" "}
              <strong>all your CPU cores</strong> for faster, stronger analysis.
            </p>
            <p>
              <strong>Easiest way — the desktop app.</strong> If you installed
              the Chess Tree Analyzer desktop app (the double-click installer),
              just click <em>My own engine (local)</em>, then{" "}
              <em>Browse…</em>, and pick your engine program from the file window
              (on Windows it ends in <code>.exe</code>). It connects
              automatically — no terminal, no typing file paths.
            </p>
            <p>
              <strong>In the browser version</strong> you start a small helper
              first, because a web page cannot launch a program on its own:
            </p>
            <ol>
              <li>
                Open a terminal in the project folder and run{" "}
                <code>npm run bridge</code>. This starts a small helper that lets
                the app launch your engine. (Or run <code>npm run dev:full</code>{" "}
                to start the app and the helper together.) Leave that window
                open.
              </li>
              <li>
                In the <em>Engine</em> card, click{" "}
                <em>My own engine (local)</em>, paste the full path to your
                engine program (on Windows it usually ends in{" "}
                <code>.exe</code>), and press <em>Enter</em> — it connects
                automatically.
              </li>
              <li>
                When the status in the top-right shows your engine’s name, you’re
                connected. The app remembers your choice for next time.
              </li>
            </ol>
            <p className="help-tip">
              Everything still stays on your computer — your engine runs only on
              your machine and is not reachable from the internet. If you publish
              the app online, visitors automatically use the built-in browser
              engine.
            </p>
          </section>

          <section id="help-settings">
            <h3>Analysis settings</h3>
            <p>
              These sliders control how wide and how deep the tree gets, and how
              hard the engine works. Bigger numbers usually mean a more thorough
              analysis but a longer wait.
            </p>
            <ul className="help-defs">
              <li>
                <strong>Max depth (half-moves):</strong> how many moves deep the
                tree goes. A “half-move” is one move by one player, so a depth of
                4 means about two full moves for each side. Higher = deeper tree,
                more time.
              </li>
              <li>
                <strong>Time per position:</strong> how long the engine thinks
                about each position, in milliseconds (1000 ms = 1 second). More
                time = stronger, more reliable moves, but slower overall.
              </li>
              <li>
                <strong>White moves / Black moves:</strong> how many candidate
                moves to keep for that side at each position. For example,
                setting White moves to 3 explores up to the top 3 moves for
                White. You can set different counts for each colour.
              </li>
              <li>
                <strong>White threshold / Black threshold (cp):</strong> a
                quality filter measured in centipawns (see the glossary). A move
                is only kept if it’s within this many centipawns of the best
                move for that side. A smaller number keeps only near-best moves;
                a larger number keeps more alternatives. You can set this
                separately for each colour.
              </li>
              <li>
                <strong>Engine hash:</strong> how much memory (in MB) the engine
                may use to remember positions it has already worked out. More can
                help on big analyses; the default is fine for most uses. The
                built-in browser engine is limited to a modest amount; if you
                connect your own engine, the slider opens up to what your computer
                can spare.
              </li>
              <li>
                <strong>Engine threads:</strong> how many CPU cores the engine
                uses. The built-in browser engine runs single-threaded, so this
                is fixed at 1. If you connect your own engine (see{" "}
                <em>Choosing your engine</em>), you can raise this to use more
                cores for faster analysis.
              </li>
            </ul>
          </section>

          <section id="help-board">
            <h3>The board &amp; navigation</h3>
            <p>
              The board in the middle always shows the position for whatever move
              you’ve selected. Below it:
            </p>
            <ul className="help-defs">
              <li>
                <strong>Back:</strong> step to the move before the current one
                (its “parent” in the tree).
              </li>
              <li>
                <strong>Forward:</strong> step into the first follow-up move of
                the current one.
              </li>
            </ul>
            <p>
              Under the buttons you’ll see the selected move’s name and the FEN
              code for that exact position, which you can copy if you need it
              elsewhere.
            </p>
          </section>

          <section id="help-tree">
            <h3>The variation tree</h3>
            <p>
              The panel on the right shows every line the analysis found as
              flowing chess notation, just like ChessBase and other chess
              software. <strong>Click any move to jump straight to that position
              on the board.</strong> The move you’re currently viewing is
              highlighted.
            </p>
            <ul className="help-defs">
              <li>
                <strong>Bold moves</strong> are the main line — the engine’s top
                continuation running straight through.
              </li>
              <li>
                Moves in <span className="help-blue">blue</span> are the moves
                from your original game or starting line.
              </li>
              <li>
                <strong>Side-variations</strong> are alternative moves the engine
                suggested. They appear in brackets right after the move they’re an
                alternative to — <code>( )</code> for the first level,{" "}
                <code>[ ]</code> and <code>{"{ }"}</code> for deeper nesting.
              </li>
              <li>
                The small <strong>+ / −</strong> button before a variation folds
                it away or opens it back up, so you can hide branches you’re not
                looking at.
              </li>
            </ul>
            <p>
              Each analysed move also shows a small evaluation next to it — see
              below.
            </p>
          </section>

          <section id="help-evals">
            <h3>How evaluations are shown</h3>
            <p>
              Every analysed move shows a small coloured evaluation next to it.
              Evaluations are always given from{" "}
              <strong>White’s point of view</strong>:
            </p>
            <ul className="help-defs">
              <li>
                A <strong>positive</strong> number (e.g. <code>+0.80</code>)
                means White is better.
              </li>
              <li>
                A <strong>negative</strong> number (e.g. <code>-1.20</code>)
                means Black is better.
              </li>
              <li>
                Numbers are in pawns: <code>+1.00</code> is roughly the value of
                one extra pawn (100 centipawns).
              </li>
              <li>
                A value like <code>#3</code> (or <code>#-3</code>) means a
                forced checkmate in that many moves.
              </li>
            </ul>
          </section>

          <section id="help-export">
            <h3>Saving your results</h3>
            <p>
              After an analysis finishes, a download button appears on the left:
            </p>
            <ul className="help-defs">
              <li>
                <strong>PGN:</strong> saves the whole tree as a standard PGN
                file with all variations and evaluation comments. You can open
                this in ChessBase, Lichess, SCID, and most other chess programs.
              </li>
            </ul>
            <p>
              You can also stop a long analysis early with <em>Stop
              Analysis</em> — whatever has been worked out so far is kept.
            </p>
          </section>

          <section id="help-glossary">
            <h3>Glossary</h3>
            <ul className="help-defs">
              <li>
                <strong>PGN:</strong> Portable Game Notation — the standard text
                format for writing down a chess game.
              </li>
              <li>
                <strong>FEN:</strong> Forsyth–Edwards Notation — a short code
                that describes a single board position exactly.
              </li>
              <li>
                <strong>Centipawn (cp):</strong> one hundredth of a pawn, used to
                measure small advantages. 100 cp = one pawn’s worth.
              </li>
              <li>
                <strong>Half-move (ply):</strong> a single move by one player.
                Two half-moves (one by each side) make a full move.
              </li>
              <li>
                <strong>Main line:</strong> the primary sequence of moves —
                here, the moves from your input game or starting line.
              </li>
              <li>
                <strong>Variation:</strong> an alternative branch of moves
                exploring a different way the game could go.
              </li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
}
