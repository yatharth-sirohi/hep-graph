"""Hand-picked seed identities used to warm routing, never to weigh the graph.

These names are cache and routing-priority candidates only.  Membership is not
a ranking, changes no hop cost, and can never change a shortest distance: the
set is consulted solely to break ties between people already at the same
search depth, and to skip a name lookup for a hot endpoint.

Resolution is deliberately conservative.  A name that returns more than one
plausible profile is recorded as ambiguous and left out rather than guessed.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Iterable

MAX_SEEDS = 800
_ID = re.compile(r"[1-9][0-9]{0,11}")

HISTORICAL = (
    "Albert Einstein", "Niels Bohr", "Paul Dirac", "Richard Feynman", "Werner Heisenberg",
    "Erwin Schrödinger", "Wolfgang Pauli", "Max Born", "Enrico Fermi", "J. Robert Oppenheimer",
    "Julian Schwinger", "Sin-Itiro Tomonaga", "Freeman Dyson", "Lev Landau", "Eugene Wigner",
    "Hans Bethe", "Murray Gell-Mann", "George Zweig", "Hideki Yukawa", "C. N. Yang",
    "Tsung-Dao Lee", "Abdus Salam", "Steven Weinberg", "Sheldon Glashow", "Gerard 't Hooft",
    "Martinus Veltman", "Peter Higgs", "François Englert", "Robert Brout", "Yoichiro Nambu",
    "Makoto Kobayashi", "Toshihide Maskawa", "Nicola Cabibbo", "Bruno Pontecorvo",
    "Ettore Majorana", "Victor Weisskopf", "John Wheeler", "Hermann Weyl", "Emmy Noether",
    "Arthur Eddington", "Subrahmanyan Chandrasekhar", "Georges Lemaître", "George Gamow",
    "Andrei Sakharov", "Yakov Zeldovich", "John Bardeen", "John Bell", "David Bohm",
    "Louis de Broglie", "Max Planck", "Arnold Sommerfeld", "Hendrik Lorentz", "Pascual Jordan",
    "John von Neumann", "Lise Meitner", "Otto Hahn", "Ernest Rutherford", "James Chadwick",
    "Patrick Blackett", "Cecil Powell", "Donald Glaser", "Luis Alvarez", "Willis Lamb",
    "Polykarp Kusch", "Robert Hofstadter", "Maria Goeppert Mayer", "J. Hans D. Jensen",
    "Felix Bloch", "Edward Purcell", "Isidor Rabi", "Samuel Goudsmit", "George Uhlenbeck",
    "Vladimir Fock", "Igor Tamm", "Lev Artsimovich", "Pyotr Kapitza", "Satyendra Nath Bose",
    "Paul Ehrenfest", "Vladimir Veksler", "Edwin McMillan", "John Cockcroft", "Ernest Walton",
    "Emilio Segrè", "Owen Chamberlain", "Clifford Shull", "Bertram Brockhouse", "Clyde Cowan",
    "Frederick Reines", "Raymond Davis Jr.", "Masatoshi Koshiba", "Riccardo Giacconi",
    "Vera Rubin", "Fritz Zwicky", "Chien-Shiung Wu", "Val Logsdon Fitch", "James Cronin",
    "Burton Richter", "Samuel Ting", "Harrie Massey",
)

THEORY = (
    "Edward Witten", "Juan Maldacena", "Nathan Seiberg", "Cumrun Vafa", "Leonard Susskind",
    "David Gross", "Frank Wilczek", "Hugh David Politzer", "Michael Green", "John Schwarz",
    "Joseph Polchinski", "Stephen Hawking", "Roger Penrose", "Kip Thorne", "Alan Guth",
    "Andrei Linde", "Alexei Starobinsky", "Viatcheslav Mukhanov", "Paul Steinhardt",
    "Neil Turok", "Lee Smolin", "Carlo Rovelli", "Abhay Ashtekar", "Nima Arkani-Hamed",
    "Savas Dimopoulos", "Howard Georgi", "Georgi Dvali", "Lisa Randall", "Raman Sundrum",
    "Riccardo Rattazzi", "Csaba Csaki", "Lawrence Hall", "Hitoshi Murayama", "Mark Wise",
    "John Preskill", "Sidney Coleman", "Kenneth Wilson", "Alexander Polyakov",
    "Alexander Zamolodchikov", "Alexander Belavin", "Alexander Migdal", "David Olive",
    "Peter Goddard", "Michael Atiyah", "Daniel Freedman", "Sergio Ferrara",
    "Peter van Nieuwenhuizen", "Bruno Zumino", "Julius Wess", "Stanley Deser", "Roman Jackiw",
    "Claudio Teitelboim", "Ashoke Sen", "Barton Zwiebach", "Andrew Strominger",
    "Gary Horowitz", "Eva Silverstein", "Shamit Kachru", "Tom Banks", "Brian Greene",
    "Michael Douglas", "Leonard Parker", "Robert Wald", "Sean Carroll", "Raphael Bousso",
    "David Tong", "John Cardy", "Subir Sachdev", "Xiao-Gang Wen", "Frank Verstraete",
    "Steven Kivelson", "Philip Anderson", "Pierre Ramond", "Pierre Fayet", "Mary K. Gaillard",
    "Robbert Dijkgraaf", "Erik Verlinde", "Herman Verlinde", "Shiraz Minwalla",
    "Freddy Cachazo", "Zvi Bern", "Lance Dixon", "Henriette Elvang", "Clifford Cheung",
    "David Simmons-Duffin", "Davide Gaiotto", "Gregory Moore", "Nathan Berkovits",
    "Igor Klebanov", "Matthew Strassler", "Joseph Lykken", "Jonathan Bagger", "John Terning",
    "Thomas Appelquist", "Steven Giddings", "Mark Srednicki", "Kenneth Lane", "Daniel Harlow",
    "Netta Engelhardt", "Leonardo Rastelli",
)

PHENOMENOLOGY = (
    "John Ellis", "Gian Giudice", "Graham Ross", "Keith Olive", "Joseph Silk", "Michael Dine",
    "Ann Nelson", "Michael Peskin", "Howard Haber", "Sally Dawson", "Marcela Carena",
    "Carlos Wagner", "Ian Hinchliffe", "Jonathan Feng", "Jesse Thaler", "Matthew Reece",
    "Patrick Meade", "David E. Kaplan", "Zackaria Chacko", "Tim Tait", "Graham Kribs",
    "Bogdan Dobrescu", "Dan Hooper", "Patrick Fox", "Roni Harnik", "Gordan Krnjaic",
    "Brian Batell", "David Morrissey", "Rouven Essig", "Jure Zupan", "Christopher Hill",
    "Elizabeth Simmons", "Sekhar Chivukula", "Tilman Plehn", "Michael Spira", "Gudrun Hiller",
    "Gudrun Heinrich", "Stefan Dittmaier", "Alexander Belyaev", "Fabiola Gianotti",
    "Michelangelo Mangano", "Michel Della Negra", "Lyn Evans", "Peter Jenni", "Sau Lan Wu",
    "Maria Spiropulu", "Joe Incandela", "John Huth", "Paris Sphicas", "Beate Heinemann",
    "Halina Abramowicz", "Gigi Rolandi", "Tiziano Camporesi", "Tejinder Virdee",
    "Timothy Cohen", "David Shih", "Daniel Green", "Chris Quigg", "Estia Eichten",
    "Keith Ellis", "Walter Giele", "John Campbell", "Zoltan Kunszt", "John Collins",
    "David Kosower", "Fabio Maltoni", "Olivier Mattelaer", "Johan Alwall", "Tao Han",
    "Peter Skands", "Torbjorn Sjöstrand", "Bryan Webber", "Giuseppe Marchesini",
    "Stefano Frixione", "Paolo Nason", "Uli Baur", "Keith Hamilton", "Simon Plätzer",
    "Frank Krauss", "Michael Krämer", "Aude Gehrmann-De Ridder", "Thomas Gehrmann",
    "Emanuele Re", "Stefano Catani", "Massimiliano Grazzini", "Giulia Zanderighi",
    "Claude Duhr", "Johannes Henn", "Bernhard Mistlberger", "Fabio Zwirner",
    "Andreas Crivellin", "David Straub", "Wolfgang Altmannshofer", "Andrzej Buras",
    "Gerhard Buchalla", "Matthias Neubert", "Thomas Becher", "Thomas Mannel",
    "Alexander Lenz", "Michael Graesser",
)

NEUTRINO = (
    "John Bahcall", "John Beacom", "Francis Halzen", "Carlos Argüelles", "Matheus Hostert",
    "Kevin Kelly", "Pedro Machado", "André de Gouvêa", "Peter Denton", "Shirley Li",
    "Patrick Huber", "Shunsaku Horiuchi", "Gail McLaughlin", "James Kneller", "Huaiyu Duan",
    "George Fuller", "Yong-Zhong Qian", "Silvia Pascoli", "Serguey Petcov", "Joachim Kopp",
    "Bhupal Dev", "Rabindra Mohapatra", "Manfred Lindner", "Werner Rodejohann",
    "Julia Gehrlein", "Vedran Brdar", "Ian Shoemaker", "Louis Strigari", "Mary Hall Reno",
    "Noemi Rocco", "Joshua Isaacson", "Bhaskar Dutta", "Renata Zukanovich Funchal",
    "Olga Mena", "Sergio Palomares-Ruiz", "Michel Sorel", "Alexander Friedland",
    "Mauricio Bustamante", "Francis-Yan Cyr-Racine", "Kate Scholberg", "Mark Messier",
    "Janet Conrad", "Boris Kayser", "Stephen Parke", "Stephen Barr", "Alexei Smirnov",
    "Eligio Lisi", "Francesco Vissani", "Francesco Capozzi", "Thomas Schwetz",
    "Michele Maltoni", "Ivan Esteban", "Ivan Martinez-Soler", "Yuber Perez-Gonzalez",
    "Hisakazu Minakata", "Tommy Ohlsson", "Walter Winter", "Evgeny Akhmedov",
    "Alexander Kusenko", "Yasaman Farzan", "Amol Dighe", "Basudeb Dasgupta", "Georg Raffelt",
    "Günter Sigl", "Thomas K. Gaisser", "Teresa Montaruli", "Eli Waxman",
    "Maria Gonzalez-Garcia", "Kohta Murase", "Ke Fang", "Markus Ahlers", "Spencer Klein",
    "Dawn Williams", "Naoko Kurahashi Neilson", "Tyce DeYoung", "Carsten Rott", "Juan Collar",
    "Juan Formaggio", "Karsten Heeger", "Georgia Karagiorgi", "Bonnie Fleming",
    "Mayly Sanchez", "Deborah Harris", "Sam Zeller", "Ryan Patterson", "Chris Marshall",
    "Giles Barr", "Mark Thomson", "Yifang Wang", "Jun Cao", "Kam-Biu Luk", "Takaaki Kajita",
    "Arthur McDonald", "Yoichiro Suzuki", "Masayuki Nakahata", "Atsuto Suzuki",
    "Koichiro Nishikawa", "Yoshi Uchida", "Pilar Hernández", "Laura Baudis",
)

EXPERIMENT = (
    "Carlo Rubbia", "Georges Charpak", "Simon van der Meer", "Jack Steinberger",
    "Leon Lederman", "Melvin Schwartz", "Martin Perl", "David Nygren", "Barry Barish",
    "Rainer Weiss", "Rolf-Dieter Heuer", "Sergio Bertolucci", "Robert Aymar",
    "Luciano Maiani", "Herwig Schopper", "Dario Barberis", "Dave Charlton", "Karl Jakobs",
    "Andreas Hoecker", "Marumi Kado", "Patricia McBride", "Joel Butler",
    "Günther Dissertori", "Albert De Roeck", "Guy Wilkinson", "Tatsuya Nakada",
    "Sheldon Stone", "Patrick Koppenburg", "Monica Pepe-Altarelli", "Chris Parkes",
    "Tara Shears", "Neville Harnew", "Mike Williams", "Giovanni Passaleva", "Luciano Musa",
    "Paolo Giubellino", "Johanna Stachel", "Jürgen Schukraft", "Federico Antinori",
    "Marco van Leeuwen", "Peter Braun-Munzinger", "Berndt Müller", "Wit Busza",
    "Krishna Rajagopal", "David d'Enterria", "Jamie Nagle", "Gunther Roland", "Ulrich Heinz",
    "Marek Gazdzicki", "Reinhard Stock", "Thomas Peitzmann", "John Harris", "Barbara Jacak",
    "Toru Iijima", "Tom Browder", "Adrian Bevan", "Michael Roney", "Yasuyuki Horii",
    "Tomio Kobayashi", "Hitoshi Yamamoto", "David Hitlin", "Jonathan Dorfan",
    "Nigel Lockyer", "Lia Merminga", "Young-Kee Kim", "Pier Oddone", "John Peoples",
    "Robert Wilson", "Helen Edwards", "Alvin Tollestrup", "Maury Tigner", "Robert Palmer",
    "Vladimir Shiltsev", "Michael Lamont", "Brennan Goddard", "Mike Seidel",
    "Frank Zimmermann", "Oliver Brüning", "Lucio Rossi", "Ezio Todesco", "Mike Benedikt",
    "Steinar Stapnes", "Philip Bryant", "Akira Yamamoto", "Shin-ichi Kurokawa",
    "Andrew Sessler", "Alexander Chao", "Katsunobu Oide", "Pantaleo Raimondi",
    "Masashi Hazumi", "Peter Križan", "Achim Stahl", "Joachim Mnich", "Brian Foster",
    "David South", "Chiara Mariotti", "Joel Primack", "Ian Shipsey", "Patricia Burchat",
    "Natalie Roe",
)

SEEDS: tuple[str, ...] = HISTORICAL + THEORY + PHENOMENOLOGY + NEUTRINO + EXPERIMENT


def _candidates(response: Any) -> list[dict[str, Any]]:
    hits = (response or {}).get("hits", {}).get("hits", [])
    found = []
    for hit in hits if isinstance(hits, list) else []:
        identifier = str(hit.get("id", ""))
        metadata = hit.get("metadata") or {}
        if not _ID.fullmatch(identifier) or str(metadata.get("control_number", "")) != identifier:
            continue
        name = (metadata.get("name") or {}).get("value") or ""
        found.append({"id": identifier, "name": name})
    return found


def resolve(client: Any, names: Iterable[str], *, query_for,
            progress=None) -> dict[str, Any]:
    """Resolve seed names through the shared broker, one request per name.

    A name is kept only when exactly one public profile answers for it.  Every
    other outcome is recorded with its reason and left unresolved: a seed is a
    convenience, and guessing one would put a wrong identity on a hot path.
    """
    resolved: dict[str, str] = {}
    ambiguous: dict[str, list[dict[str, Any]]] = {}
    missing: list[str] = []
    failed: dict[str, str] = {}
    for name in names:
        if len(resolved) >= MAX_SEEDS:
            break
        try:
            found = _candidates(client.search("authors", query_for(name), size=5, page=1))
        except Exception as error:
            failed[name] = f"{type(error).__name__}: {error}"
        else:
            if len(found) == 1:
                resolved[name] = found[0]["id"]
            elif found:
                ambiguous[name] = found
            else:
                missing.append(name)
        if progress is not None:
            progress(name)
    return {"resolved": resolved, "ambiguous": ambiguous, "missing": missing, "failed": failed}


def load(path: str | Path) -> frozenset[str]:
    """Read a previously resolved seed file, or nothing if there is none.

    A missing or unreadable file is not an error: seeds only reorder equal-depth
    work, so the application must start and search correctly without them.
    """
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return frozenset()
    values = data.get("resolved") if isinstance(data, dict) else None
    if not isinstance(values, dict):
        return frozenset()
    return frozenset(str(item) for item in list(values.values())[:MAX_SEEDS]
                     if _ID.fullmatch(str(item)))
