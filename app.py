import random
import statistics
import matplotlib.pyplot as plt
import streamlit as st



st.set_page_config(
    page_title="Braess's Paradox Simulation",
    page_icon="🚦",
    layout="wide"
)

st.title("Braess's Paradox")
st.subheader("Can adding a road make traffic slower?")

st.write(
    "Explore how adding a shortcut to a road network can affect "
    "the average travel time of vehicles."
)

st.info(
    "The simulation compares the network without a shortcut "
    "against the network with a shortcut."
)


st.header("Road Networks")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Without Shortcut")

    st.graphviz_chart("""
    graph {
        rankdir=LR;
        A -- B [label="Congested"];
        A -- C [label="18 min"];
        B -- D [label="18 min"];
        C -- D [label="Congested"];
        {rank=same; B; C}
    }
    """)



with col2:
    st.subheader("2. With Shortcut")

    st.graphviz_chart("""
    graph {
        rankdir=LR;
        A -- B [label="Congested"];
        A -- C [label="18 min"];
        B -- D [label="18 min"];
        C -- D [label="Congested"];
        B -- C [color=red, penwidth=3];
        {rank=same; B; C}
    }
    """)

    st.markdown("🔴 **Shortcut (B ↔ C): 2 minutes**")




with st.expander("Road Network and Model Assumptions", expanded=True):
    st.subheader("Road travel-time rules")

    st.markdown("""
    - **A → B:** 5 + (0.15 × vehicles on the road) minutes
    - **A → C:** 18 minutes (fixed)
    - **B → D:** 18 minutes (fixed)
    - **C → D:** 5 + (0.15 × vehicles on the road) minutes
    - **B ↔ C:** 2 minutes (fixed shortcut)
    """)

    st.subheader("Route-selection probabilities")

    st.markdown("**Without the shortcut**")
    st.write("A → B → D: 50%")
    st.write("A → C → D: 50%")

    st.markdown("**With the shortcut**")
    st.write("A → B → D: 22%")
    st.write("A → C → D: 22%")
    st.write("A → B → C → D: 50%")
    st.write("A → C → B → D: 6%")

    st.caption(
        "These probabilities are illustrative assumptions, not "
        "measured driver behaviour. Each vehicle is assigned a route "
        "randomly using the selected probabilities. The model does "
        "not dynamically reroute drivers based on congestion."
    )



class Road:
    def __init__(self, name, road_type, base_time, congestion_factor=0):
        self.name = name
        self.road_type = road_type
        self.base_time = base_time
        self.congestion_factor = congestion_factor

    def travel_time(self, vehicles):
        if self.road_type == "congested":
            return self.base_time + self.congestion_factor * vehicles

        return self.base_time



def create_network(with_shortcut=False):
    roads = {
        "AB": Road("A → B", "congested", 5, 0.15),
        "AC": Road("A → C", "fixed", 18),
        "BD": Road("B → D", "fixed", 18),
        "CD": Road("C → D", "congested", 5, 0.15),
    }

    if with_shortcut:
        roads["BC"] = Road("B ↔ C", "fixed", 2)

    return roads






def define_routes(with_shortcut=False):
    routes = {
        "A → B → D": ["AB", "BD"],
        "A → C → D": ["AC", "CD"],
    }

    if with_shortcut:
        routes["A → B → C → D"] = ["AB", "BC", "CD"]
        routes["A → C → B → D"] = ["AC", "BC", "BD"]

    return routes



def calculate_road_traffic(routes, route_vehicles):
    road_traffic = {}

    for route, road_names in routes.items():
        vehicles = route_vehicles[route]

        for road in road_names:
            road_traffic[road] = (
                road_traffic.get(road, 0) + vehicles
            )

    return road_traffic


def calculate_route_times(roads, routes, road_traffic):
    route_times = {}

    for route, road_names in routes.items():
        route_times[route] = sum(
            roads[name].travel_time(road_traffic.get(name, 0))
            for name in road_names
        )

    return route_times






def calculate_route_probabilities(route_times):
    if "A → B → C → D" in route_times:
        return {
            "A → B → D": 0.22,
            "A → C → D": 0.22,
            "A → B → C → D": 0.50,
            "A → C → B → D": 0.06,
        }

    return {
        "A → B → D": 0.50,
        "A → C → D": 0.50,
    }








def distribute_vehicles(total_vehicles, probabilities):
    routes = list(probabilities.keys())
    weights = list(probabilities.values())

    assignments = random.choices(
        routes,
        weights=weights,
        k=total_vehicles
    )

    route_vehicles = {route: 0 for route in routes}

    for route in assignments:
        route_vehicles[route] += 1

    return route_vehicles




def calculate_average_time(route_times, route_vehicles):
    total_vehicles = sum(route_vehicles.values())

    if total_vehicles == 0:
        return 0

    total_travel_time = sum(
        route_times[route] * route_vehicles[route]
        for route in route_times
    )

    return total_travel_time / total_vehicles



def simulate(total_vehicles, with_shortcut):
    roads = create_network(with_shortcut)
    routes = define_routes(with_shortcut)

    # Fixed probabilities represent drivers' expectations.
    route_times_placeholder = {route: 0 for route in routes}
    probabilities = calculate_route_probabilities(
        route_times_placeholder
    )

    # Randomly assign each vehicle exactly once.
    route_vehicles = distribute_vehicles(
        total_vehicles,
        probabilities
    )

    # Calculate traffic on each road from the assigned routes.
    road_traffic = calculate_road_traffic(
        routes,
        route_vehicles
    )

    # Calculate the resulting travel time for every route.
    route_times = calculate_route_times(
        roads,
        routes,
        road_traffic
    )

    average_time = calculate_average_time(
        route_times,
        route_vehicles
    )

    return {
        "routes": routes,
        "route_vehicles": route_vehicles,
        "road_traffic": road_traffic,
        "route_times": route_times,
        "probabilities": probabilities,
        "average_time": average_time
    }


def display_results(title, results):
    print(f"\n{title}")

    for route in results["routes"]:
        print(
            f"{route}: "
            f"{results['route_vehicles'][route]:.2f} vehicles, "
            f"{results['route_times'][route]:.2f} minutes"
        )

    print(
        f"Average travel time: "
        f"{results['average_time']:.2f} minutes"
    )



st.header("Simulation Settings")

total_vehicles = st.selectbox(
    "Total number of vehicles",
    [50, 100, 200, 500, 1000],
    index=2
)

num_runs = st.selectbox(
    "Number of simulation runs",
    [1, 2, 3, 4, 5],
    index=4
)

st.caption(
    "More runs provide a more stable comparison, "
    "but take slightly longer."
)

run_simulation = st.button(
    "Run Simulation",
    type="primary"
)



if run_simulation:
    without_shortcut_runs = []
    with_shortcut_runs = []

    for run in range(num_runs):
        without_shortcut = simulate(total_vehicles, False)
        with_shortcut = simulate(total_vehicles, True)

        without_shortcut_runs.append(without_shortcut)
        with_shortcut_runs.append(with_shortcut)

    without_times = [
        result["average_time"]
        for result in without_shortcut_runs
    ]

    with_times = [
        result["average_time"]
        for result in with_shortcut_runs
    ]

    mean_without = statistics.mean(without_times)
    mean_with = statistics.mean(with_times)

    change = mean_with - mean_without

    median_without = statistics.median(without_times)
    median_with = statistics.median(with_times)

    std_without = statistics.pstdev(without_times)
    std_with = statistics.pstdev(with_times)

    min_without = min(without_times)
    max_without = max(without_times)

    min_with = min(with_times)
    max_with = max(with_times)

    st.header("Simulation Results")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Without Shortcut",
            f"{mean_without:.2f} minutes"
        )

    with col2:
        st.metric(
            "With Shortcut",
            f"{mean_with:.2f} minutes",
            delta=f"{change:+.2f} minutes",
            delta_color="inverse"
        )

    if change > 0:
        st.warning(
            "Average travel time increased after adding "
            "the shortcut in these simulation runs."
        )
    elif change < 0:
        st.success(
            "Average travel time decreased after adding "
            "the shortcut in these simulation runs."
        )
    else:
        st.info("There was no change in average travel time.")



    col1, col2 = st.columns(2)

    # Graph 1: Bar chart
    with col1:
        st.subheader("Average Travel Time Comparison")

        fig, ax = plt.subplots(figsize=(6, 4))

        ax.bar(
            ["Without Shortcut", "With Shortcut"],
            [mean_without, mean_with]
        )

        ax.set_ylabel("Average Travel Time (minutes)")
        ax.set_title("Effect of Adding a Shortcut")
        ax.tick_params(axis="x", labelrotation=10)

        st.pyplot(fig)
        plt.close(fig)

    # Graph 2: Line chart
    with col2:
        st.subheader("Travel Time Across Simulation Runs")

        fig2, ax2 = plt.subplots(figsize=(6, 4))

        run_numbers = list(range(1, num_runs + 1))

        ax2.plot(
            run_numbers,
            without_times,
            marker="o",
            label="Without Shortcut"
        )

        ax2.plot(
            run_numbers,
            with_times,
            marker="o",
            label="With Shortcut"
        )

        ax2.set_xlabel("Simulation Run")
        ax2.set_ylabel("Average Travel Time (minutes)")
        ax2.set_title("Travel Time Across Simulation Runs")
        ax2.set_xticks(run_numbers)
        ax2.legend()

        st.pyplot(fig2)
        plt.close(fig2)



    st.subheader("Results by Simulation Run")

    st.dataframe(
        {
            "Run": list(range(1, num_runs + 1)),
            "Without Shortcut (min)": [
                round(t, 2) for t in without_times
            ],
            "With Shortcut (min)": [
                round(t, 2) for t in with_times
            ],
        },
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Summary Statistics")

    st.dataframe(
        {
            "Statistic": [
                "Mean", "Median", "Standard deviation",
                "Minimum", "Maximum"
            ],
            "Without Shortcut (min)": [
                round(mean_without, 2),
                round(median_without, 2),
                round(std_without, 2),
                round(min_without, 2),
                round(max_without, 2),
            ],
            "With Shortcut (min)": [
                round(mean_with, 2),
                round(median_with, 2),
                round(std_with, 2),
                round(min_with, 2),
                round(max_with, 2),
            ],
        },
        hide_index=True,
        use_container_width=True
    )







