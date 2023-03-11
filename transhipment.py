from pulp import *
import sys


def main():
    # STDOUT to log.txt
    with open("log.txt", 'w') as f:
        sys.stdout = f

        # Indices
        mills = list(range(3))
        warehouses = list(range(4))
        customer_areas = list(range(13))

        # Parameters
        production_capacities = [9900, 2100, 4200]
        extra_capacities = [1100, 1400, 1500]
        customer_area_demands = [650, 260, 650, 130, 780, 2500, 910, 3120, 910, 3640, 1040, 1650, 1780]

        # Transportation costs from mills to warehouses
        transport_costs_WH = [[53, 95, 136, 160],
                              [60, 120, 132, 140],
                              [210, 190, 89, 71]]

        # Transportation costs from warehouses to customers
        transport_costs_customers = [[100, 120, 150, 160, 300, 310, 340, 490, 430, 360, 280, 350, 200],
                                     [200, 240, 280, 310, 280, 400, 440, 410, 380, 190, 80, 150, 90],
                                     [280, 260, 320, 400, 140, 319, 290, 240, 230, 80, 60, 60, 160],
                                     [320, 280, 200, 130, 130, 70, 100, 90, 100, 190, 370, 320, 390]]
        # Extra capacity costs
        extra_capacity_costs = [300000, 400000, 450000]

        # Create a optimization model (minimization)
        model = LpProblem("PP_MILP_model", LpMinimize)

        # Create decision variables x_ik
        x = [[LpVariable("x_" + str(i) + str(k), 0, None) for k in warehouses] for i in mills]

        # Create decision variables y_kj
        y = [[LpVariable("y_" + str(k) + str(j), 0, None) for j in customer_areas] for k in warehouses]

        # Create decision variables z_i
        z = [LpVariable("z_" + str(i), cat="Binary") for i in mills]

        # Add objective function
        model += (
            lpSum(x[k][j] * transport_costs_WH[k][j] for j in warehouses for k in mills) +
            lpSum(y[k][j] * transport_costs_customers[k][j] for j in customer_areas for k in warehouses) +
            lpSum(z[i] * extra_capacity_costs[i] for i in mills)
            , "transportation_costs")

        # Add Constraint 1 to model object
        for i in mills:
            model += (
                    lpSum(x[i][k] for k in warehouses) <= production_capacities[i] + z[i] * extra_capacities[i])

            # Constraint 2
        for k in warehouses:
            model += (
                    lpSum(x[i][k] for i in mills) == lpSum(y[k][j] for j in customer_areas))

        # Constraint 3
        for j in customer_areas:
            model += (
                    lpSum([y[k][j] for k in warehouses]) == customer_area_demands[j])

        model.solve()  # Solve the model

        # Print optimal objective function value:
        print("Optimal total cost " + str(model.objective.value()) + " .")

        # Print optimal decision variable values:
        for i in mills:
            print("------")
            if z[i].varValue == 1:  # if extra capacity is bought, it is reported to the output file
                print("Purchase extra capacity for mill " + str(i))
            for k in warehouses:
                if x[i][k].varValue > 0:  # Only routes with actual traffic are written to file
                    print("Transport " + str(x[i][k].varValue) + " tons of carton from mill " + str(
                        i) + " to warehouse " + str(
                        k) + ".")

        print("---------------")
        for k in warehouses:
            for j in customer_areas:
                if y[k][j].varValue > 0:  # Only routes with actual traffic are written to file
                    print("Transport " + str(y[k][j].varValue) + " tons of carton from warehouse " + str(
                        k) + " to customer area " + str(j) + ".")
            print("---")


# Boilerplate code to run the script
if __name__ == "__main__":
    main()
