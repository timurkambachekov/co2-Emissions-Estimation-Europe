import PySimpleGUI as sg
import co2_map

# All the stuff inside your window.
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December']
years = [2015, 2016, 2017, 2018, 2019]
resolution = [i for i in range(5, 21)]
plots = ['Predictions', 'Error']

month_selected, year_selected, resolution_selected, mae, plot_selected = 0, 2018, 5, 0, 'Predictions'

column1 = [
    [sg.Text('Predicted Emissions Map')],
    [sg.Graph((1000, 400), (0, 0), (1000, 400), key='-GRAPH-')]
]

column2 = [
    [sg.Text('Choose plot')],
    [sg.DD(plots, enable_events=True, key='-PLOT-')],
    [sg.Text('Choose a year')],
    [sg.DD(years, enable_events=True, key='-YEAR-')],
    [sg.Text('Choose a month')],
    [sg.DD(months, enable_events=True, key='-MONTH-')],
    [sg.Text('Set resolution')],
    [sg.DD(resolution, enable_events=True, key='-RESOLUTION-')],
    [sg.Button(button_text='Set', enable_events=True, key='-SET_TIME-')],
    [sg.Text(f'MAE: {mae}', key='-MAE-')],
]
layout = [
    [
        sg.Column(column1),
        sg.Column(column2),
    ]
]


# Create the Window
window = sg.Window('Geospatial predictions', layout, finalize=True, element_justification="center", location=(0, 0),)
figure_agg = None

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
        break

    if event == '-SET_TIME-':
        if figure_agg:
            co2_map.delete_figure_agg(figure_agg)

        year_selected = values['-YEAR-']
        month_selected = months.index(values['-MONTH-'])
        resolution_selected = values['-RESOLUTION-']
        plot_selected = values['-PLOT-']
        gdf, mae = co2_map.get_data(year_selected, month_selected)
        if plot_selected == 'Predictions':
            fig = co2_map.plot_emission_map(gdf, resolution_selected)
        else:
            fig = co2_map.plot_emission_diff_map(gdf)
        figure_agg = co2_map.draw_figure(window["-GRAPH-"].TKCanvas, fig)
        window['-MAE-'].update(f'MAE: {mae}')

window.close()
