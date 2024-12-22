from flet import *
import flet 
import time
import math
import json
from sentiment import predict_sentiment
from chatbot import generate_chatbot_response 

class MenuDetail(UserControl):
    def __init__(self):
        super().__init__()
        self.back_btn = Container(
            Icon(
                Icons.ARROW_BACK_OUTLINED,
                size = 29,
                color = 'black'
            ),
        )
        self.menu = Container(
            Stack(
                [
                    Container(
                        Row(
                            [self.back_btn],
                            alignment=MainAxisAlignment.START,
                        ),
                        height=60,
                    ),
                    Container(
                        alignment=alignment.center,
                        content=Text(
                            value="Details",
                            size=20,
                            color="black",
                            text_align=TextAlign.CENTER,
                            font_family = "font_name",
                            weight = FontWeight.BOLD
                        ),
                    ),
                ]
            ),
            height = 60,
            padding = padding.only(0, 10, 10, 0),
            margin = margin.only(left=15,right=15),
            border = border.only(bottom=border.BorderSide(1, "black")),
        )
    def build(self):
        return self.menu
    
def get_labels_with_threshold(senti_list, senti_labels, threshold_percentage=0.1):
    total_value = sum(senti_list)
    threshold_value = total_value * threshold_percentage 

    paired_list = list(zip(senti_list, senti_labels))
    paired_list.sort(reverse=True, key=lambda x: x[0])

    # Categorize “Others” for small values
    others_value = 0
    others_label = "Others"
    
    # List of colors for each label
    colors = [
        "#3673FF",  
        "#6236FF",  
        "#36B9FF",  
        "#C43AF7",  
        "#3AF7EA",  
        "#C1BEFD", 
    ]
    
    # Filter labels that are smaller than the threshold and not 0
    filtered_list = []
    small_labels = []
    color_index = 0

    for value, label in paired_list:
        if value == 0 or value < threshold_value:
            small_labels.append((value, label)) 
        else:
            filtered_list.append({
                "name": label, 
                "color": colors[color_index], 
                "values": [value]
            })
            color_index += 1

    # If there is more than one label that is smaller than the threshold, merge them into the “Others” category.
    if len(small_labels) > 1:
        others_value = sum([v for v, _ in small_labels]) 
        filtered_list.append({
            "name": others_label, 
            "color": colors[color_index],
            "values": [others_value]
        })
    else:
        for value, label in small_labels:
            filtered_list.append({
                "name": label,
                "color": colors[color_index],
                "values": [value]
            })
            color_index += 1  

    return filtered_list


# Variabel global sentiment
awful = 0
poor = 0
neutral = 0
good = 0
awesome = 0
all_feedback_file = "feedback/all_feedback.json"
def count_sentiments_from_file(file_path):
    """Read the JSON file and count the number of each sentiment category."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file is not found or is empty, return the default value
        return {"awful": 0, "poor": 0, "neutral": 0, "good": 0, "awesome": 0}

    # Initialize the number of sentiments
    sentiment_count = {"awful": 0, "poor": 0, "neutral": 0, "good": 0, "awesome": 0}

    # Count the number of each sentiment
    for feedback in data.get("feedback", []):
        sentiment = feedback.get("sentiment", "").lower()
        if sentiment in sentiment_count:
            sentiment_count[sentiment] += 1

    return sentiment_count

def initialize_sentiment_counts():
    """Updates the global variable with the number of sentiments from the JSON file."""
    global awful, poor, neutral, good, awesome
    sentiment_count = count_sentiments_from_file(all_feedback_file)
    
    awful = sentiment_count["awful"]
    poor = sentiment_count["poor"]
    neutral = sentiment_count["neutral"]
    good = sentiment_count["good"]
    awesome = sentiment_count["awesome"]

# Call function for initialization
initialize_sentiment_counts()

def create_pie():
    sentiments = [awful, poor, neutral, good, awesome] 
    labels = ["Awful", "Poor", "Neutral", "Good", "Awesome"]
    
    sentiment = get_labels_with_threshold(sentiments, labels, threshold_percentage=0.1)
    return sentiment

# Function to update Pie Chart and Legend
def update_pie_chart():
    global chart, legends_container
    
    sentiment = create_pie() 
    total_value = sum([sent["values"][0] for sent in sentiment])

    # Update sections on the pie chart
    chart.sections = [
        PieChartSection(
            value=sent["values"][0],
            title=f"{(sent['values'][0] / total_value * 100):.0f}%",
            title_style=TextStyle(
                size=12, color=Colors.WHITE, weight=FontWeight.BOLD
            ),
            color=sent["color"],  
            radius=40,  
        ) for sent in sentiment
    ]
    chart.update()

    # Update legend
    legend_rows = create_legend_items(sentiment)
    legends_container.content.controls = legend_rows
    legends_container.update()

sentiment = create_pie()
total_value = sum([sent["values"][0] for sent in sentiment])  # Total score to calculate percentage

sections = [
    PieChartSection(
        value=sent["values"][0],
        # Menghitung persentase dan menampilkan sebagai label
        title=f"{(sent['values'][0] / total_value * 100):.0f}%",  
        title_style=TextStyle(
            size=12, color=Colors.WHITE, weight=FontWeight.BOLD
        ),
        color=sent["color"], 
        radius=40, 
    ) for sent in sentiment
]

def create_legend_items(sentiments):
    sentiments = [sent for sent in sentiments if sent['values'][0] > 0]
    
    total_labels = len(sentiments)

    # If there are less than 5 labels, display all on the first row
    if total_labels < 5:
        row_items = [
            Row(
                [
                    Container(
                        width=15,
                        height=15,
                        bgcolor=sent["color"], 
                        border_radius=3, 
                    ),
                    Text(
                        f" {sent['name']}",
                        size=12,
                        color="#77798D",
                    ),
                ],
                spacing=5,  
                alignment="center",
            )
            for sent in sentiments 
        ]
        
        return [
            Row(
                controls=row_items,
                alignment="center", 
                spacing=20, 
            ),
        ]
    
    # If there are 5 or more labels, split them into two lines
    if total_labels >= 5:
        first_row_items = [
            Row(
                [
                    Container(
                        width=15,
                        height=15,
                        bgcolor=sent["color"], 
                        border_radius=3, 
                    ),
                    Text(
                        f" {sent['name']}",
                        size=12,
                        color="#77798D",
                    ),
                ],
                spacing=5,  
                alignment="center",  
            )
            for sent in sentiments[:3]  
        ]
        second_row_items = [
            Row(
                [
                    Container(
                        width=15,
                        height=15,
                        bgcolor=sent["color"], 
                        border_radius=3, 
                    ),
                    Text(
                        f" {sent['name']}",
                        size=12,
                        color="#77798D",
                    ),
                ],
                spacing=5,  
                alignment="center", 
            )
            for sent in sentiments[3:] 
        ]

        # Return two rows as a list
        return [
            Row(
                controls=first_row_items,
                alignment="center", 
                spacing=20,   
            ),
            Row(
                controls=second_row_items,
                alignment="center",  
                spacing=20, 
            ),
        ]
        
# Creating a grid for legends
legend_rows = create_legend_items(sentiment)

legends_container = Container(
    content=Column(
        controls=legend_rows,  
        horizontal_alignment="center",  
        spacing=10,                      
    ),
    padding=padding.only(20, -40, 20, 10),  
)


# Function to handle hover events on pie charts
def on_chart_event(e: PieChartEvent):
    normal_radius = 40
    hover_radius = 50
    normal_title_style = TextStyle(
        size=12, color=Colors.WHITE, weight=FontWeight.BOLD
    )
    hover_title_style = TextStyle(
        size=13,
        color=Colors.WHITE,
        weight=FontWeight.BOLD,
        shadow=BoxShadow(blur_radius=2, color=Colors.BLACK54),
    )
    
    for idx, section in enumerate(chart.sections):
        if isinstance(section, PieChartSection) and idx == e.section_index:
            section.radius = hover_radius
            section.title_style = hover_title_style
        elif isinstance(section, PieChartSection):
            section.radius = normal_radius
            section.title_style = normal_title_style
    chart.update()
    
# Create pie charts
chart = PieChart(
    sections=sections,
    sections_space=5,  
    center_space_radius=60, 
    on_chart_event=on_chart_event,
    expand=True,
)

# Container to display results
ct_result = Container(
    content=Column(
        scroll="auto"
    ),
    padding = padding.only(10, 12, 12, 12),
    border_radius=10,
    width=370, 
    shadow=BoxShadow(
        spread_radius=0,            
        blur_radius=2,             
        offset=Offset(0, 2), 
        color="#E1E1E1" 
    ),
    gradient=LinearGradient(
        begin=alignment.top_left,
        end=alignment.bottom_right,
        colors=["#C7EAFE", "#D0D1FE"]
    )
)

# Wrapping container of ct_result
ct_wrapper = Container(
    content=ct_result,
    padding = padding.only(20, 5, 20, 0),
    width=390,
)

def display_result(page: Page, response_text: str):
    ct_result.content.controls.clear()
    page.update()

    # Kontainer untuk ikon dan teks
    result_container = Row(
        controls=[
            Column(
                controls=[
                    Image(src="icons/gemini.gif", width=20, height=20),  
                ],
                alignment="start",  
                spacing=10, 
            ),
            Column(
                controls=[
                    Text(value="", color="#5563FA", size=12, expand=True), 
                ],
                expand=True,  
            ),
        ],
        alignment="start",  
        vertical_alignment="start",  
        spacing=5,  
    )

    # Tambahkan kontainer ke ct_result
    ct_result.content.controls.append(result_container)
    page.update()

    # Referensi ke teks dalam kolom untuk efek mengetik
    result_text = result_container.controls[1].controls[0] 
    typing_delay = 0.02

    # Efek mengetik untuk teks respons
    for char in response_text:
        result_text.value += char
        page.update()
        time.sleep(typing_delay)

loading_animation = Container(
    content=Column(
        [
            Container(
                Image(
                    src='animation/loading-resize.gif',
                ),
                alignment=alignment.center,
                padding=padding.only(top=230),
            ),
            Container(
                Text(
                    value="Loading, please wait...",
                    size=14,
                    color="white",
                    weight="bold",
                    text_align=TextAlign.CENTER,
                ),
                alignment=alignment.center,
                padding=padding.only(top=-20),
            ),
        ],
        alignment=alignment.center,  
        horizontal_alignment="center",
    ),
    bgcolor=Colors.with_opacity(0.4, "#000000"),
    width=390,
    height=670,
    visible=False,
    alignment=alignment.center, 
    padding=padding.all(0),  
)


# File paths
positive_file = "feedback/positive_feedback.json"
negative_file = "feedback/negative_feedback.json"
all_feedback_file = "feedback/all_feedback.json"

# Function to add feedback to JSON file
def add_feedback_to_file(file_path, feedback_entry):
    with open(file_path, "r") as file:
        data = json.load(file)

    data["feedback"].append(feedback_entry)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
        

# Functions for submitting feedback and processing sentiments
def submit_feedback(e, page):
    close_sentiment(e)
    global awful, poor, neutral, good, awesome
    
    # Disable the main element (body)
    body.scroll = None
    body.update()

    
    # Show loading animation
    loading_animation.visible = True
    loading_animation.update()
    
    feedback_text = feedback_input.value.strip() 
    if not feedback_text:
        print("No feedback provided!")
        loading_animation.visible = False
        loading_animation.update()
        
        body.visible = True
        body.update()
        return

    sentiment = predict_sentiment(feedback_text) 
    print(f"Predicted sentiment: {sentiment}")

    # Update variable values based on prediction results
    if sentiment == "Awful":
        awful += 1
    elif sentiment == "Poor":
        poor += 1
    elif sentiment == "Neutral":
        neutral += 1
    elif sentiment == "Good":
        good += 1
    elif sentiment == "Awesome":
        awesome += 1

    # Create a new feedback entry
    feedback_entry = {
        "id": math.ceil(time.time()),
        "text": feedback_text,
        "sentiment": sentiment.lower()
    }
    if sentiment in ["Good", "Awesome"]:
        add_feedback_to_file(positive_file, feedback_entry)
    elif sentiment in ["Awful", "Poor"]:
        add_feedback_to_file(negative_file, feedback_entry)
        
    add_feedback_to_file(all_feedback_file, feedback_entry)

    feedback_input.value = ""
    feedback_input.update()

    loading_animation.visible = False
    loading_animation.update()

    update_pie_chart()
    new_response_text = generate_chatbot_response()
    display_result(page, new_response_text)

    
feedback_input = TextField(
    label="Share your thoughts here",
    hint_text="Please enter text here",
    multiline=True,
    border_radius=12,
    height=100,
    border_color="grey",
    color="black",
)

bs = None

def bs_dismissed(e):
    print("Dismissed!")

def show_bs(e):
    global bs
    bs.open = True
    bs.update()
    
def close_bs(e):
    global bs
    bs.open = False
    feedback_input.value = ""
    feedback_input.update()
    bs.update()

def close_sentiment(e):
    global bs
    bs.open = False
    bs.update()
    
def create_bottom_sheet(page: Page):
    return BottomSheet(
        Container(
            Column(
                [
                    Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            Text(
                                value="What can we improve?",
                                size=20,
                                weight="bold",
                                color="black",
                            ),
                            IconButton(
                                icon=Icons.CLOSE,
                                icon_size=20,
                                on_click=close_bs,
                            )
                        ],
                    ),
                    Text(
                        value="We value your feedback about this class! Share your thoughts so we can enhance the learning experience.",
                        size=16,
                        color="#52525B",
                        text_align=TextAlign.LEFT,
                    ),
                    feedback_input,
                    Container(
                        ElevatedButton(
                            text="Submit",
                            bgcolor="#6366F1",
                            width=330,
                            color="white",
                            on_click=lambda e: submit_feedback(e, page),
                        ),
                        alignment=alignment.center,
                        margin=margin.only(top=38),
                    ),
                ],
                tight=True,
            ),
            padding=padding.only(15, 15, 15, 30),
            bgcolor="white",
            border_radius=border_radius.only(top_left=20, top_right=20, bottom_left=0, bottom_right=0),
            expand=True,
            height=402,
        ),
        on_dismiss=bs_dismissed,
    )

body = Container(
    Column([
        MenuDetail(),
        Container(
            Image(
                src  = 'images/sql_course.png',
            ),
            alignment=alignment.center,
        ),
        Container(
            Row([
                Text(
                    value="Dr. Thomas Partey",
                    size=12,
                    color="black",
                )
            ]),
            padding = padding.only(20, -1, 10, 0)
        ),
        Container(
            Row([
                Text(
                    value="SQL Fundamentals",
                    size=20,
                    color="black",
                    weight = FontWeight.BOLD
                )
            ]),
            padding = padding.only(20, -10, 10, 0)
        ),
        Container(
            Text(
                value="SQL (Structured Query Language) is a powerful and widely-used language for managing and manipulating relational databases. Understanding the fundamentals of SQL is essential.",
                size=12,
                color="black",
                text_align=TextAlign.LEFT,
            ),
            padding=padding.only(20, -1, 10, 0)
        ),
        Container(
            Row([
                Text(
                    value="Student Feedback Sentiment",
                    size=20,
                    color="black",
                    weight = FontWeight.BOLD
                )
            ]),
            padding = padding.only(20, 10, 10, 0)
        ),
        Container(
            Text(
                value="Visualize the proportion of student sentiments to give an overall picture of the range of feedback received in this class.",
                size=12,
                color="black",
                text_align=TextAlign.LEFT,
            ),
            padding=padding.only(20, -1, 10, 0)
        ),
        Container(chart,
                  padding=padding.only(0, -40, 0, 0),
                  ),
        legends_container,
        Container(
            Row([
                Text(
                    value="AI Student Analyzer",
                    size=20,
                    color="black",
                    weight = FontWeight.BOLD
                )
            ]),
            padding = padding.only(20, -5, 10, 0)
        ),
        ct_wrapper,
        Container(
            content=Row(
                controls=[
                    IconButton(Icons.MESSAGE_OUTLINED, icon_size=25, icon_color="#5170FF", on_click = show_bs),
                    Column(
                        controls=[
                            Text("Share your feedback with us", size=10, weight="bold", color=Colors.BLACK),
                            Text("Let us know about your learning experience in this course", size=8, color=Colors.GREY),
                        ],
                        spacing=2,
                        alignment="start",
                    ),
                    Icon(Icons.MORE_VERT, size=20, color=Colors.BLACK),
                ],
                alignment="spaceBetween",
                vertical_alignment="center",
                spacing=10,
            ),
            padding = 10,
            bgcolor="#DDE7FF",
            margin=padding.only(left=20, right=20, top=10, bottom=30),
            border_radius=5,
            alignment=alignment.center,
        ),
    ],
    horizontal_alignment="center",
    scroll = "always",
    on_scroll_interval = 0,
    ),
    gradient = LinearGradient(
        begin = alignment.top_left,
        end = alignment.bottom_right,
        colors = ['#6366F1','white','white']
    ),
    width = 390,
    height = 670,
    alignment=alignment.center,
)

main_body = Stack(
    [
        body,  
        loading_animation,
    ]
)

def manage(page:Page):
    global bs
    
    page.window.max_width = 390
    page.window.width = 390
    page.window.max_height = 670
    page.window.height = 670
    
    page.padding = 0
    page.font = {
        "font_name":"fonts/PlusJakartaSans.ttf"
    }
    page.theme = Theme(font_family = "font_name")
    
    bs = create_bottom_sheet(page)
    page.overlay.append(bs)
    
    page.add(
        main_body 
    )
    
    initial_response_text = generate_chatbot_response()
    display_result(page, initial_response_text)

flet.app(manage, view=AppView.WEB_BROWSER, assets_dir="assets",port=5555,)