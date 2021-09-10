#include <math.h>

double map_num(double value, double max, double wanted_min, double wanted_max) {
	return ((value / max) *(wanted_max - wanted_min)) + wanted_min;
}

double log_2(double x) {
	return log(x) / log(2);
}

double does_converge(double x_0, double y_0, int iterations) {
	double i = 0; // iter


	int color = 0;
	double x = 0;
	double y = 0;

	double x_2 = 0;
	double y_2 = 0;
	double w = 0;

	while ((i < iterations) && ((x_2 + y_2) <= 16)) {


		x = x_2 - y_2 + x_0;
		y = w - x_2 - y_2 + y_0;
		x_2 = x * x;
		y_2 = y * y;
		w = (x + y)*(x + y);

		i++;

	}
	if (i == iterations)
		return -1;
	else {
		//double smoothed = log_2(log_2(x_2 + y_2) / 2);
		double smoothed = log(log(x_2 + y_2))/log(2);
		//i = (double)(sqrt(i + 10 - smoothed));
		return sqrt(i + 10 - smoothed);
	}

}
