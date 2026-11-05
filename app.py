from flask import Flask, render_template, request

from elastic_search.search_query import search_query


app = Flask(__name__)


def get_relevance(score: float):
    if score >= 0.52:
        return "high"
    elif score >= 0.49:
        return "medium"
    return "low"


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        if query:
            results = search_query(query)

            for result in results:
                result["relevance"] = get_relevance(
                    float(result.get("score", 0))
                )

    return render_template(
        "index.html",
        results=results,
        query=query,
    )


if __name__ == "__main__":
    app.run(debug=True)