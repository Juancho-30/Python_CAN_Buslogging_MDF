from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch, cm
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from datetime import date

def create_pdf(path, title):
    c = canvas.Canvas(f"{path}/{title}.pdf", pagesize = landscape(letter))
    return c

def add_title(c, text, pos):
    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(100, pos-20, text)
    up_pos = pos - 50
    return c, up_pos

def add_subtitle(c, text, pos):
    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 25)
    c.drawString(5, pos, text)
    up_pos = pos - 35
    return c, up_pos

def add_text(c, text, pos):
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 14)
    c.drawString(5, pos, text)
    up_pos = pos - 25
    return c, up_pos

def add_metadata(c, weather, pos):
    today = date.today().strftime("%B %d, %Y")
    heute = f"Date: {today}"
    battery_number = f"Battery number: 3"
    field = f"Field: To be determined"
    work_type = "Work Type: To be extracted from Excel file"
    weather = f'Type of weather: {weather}'
    [c,pos] = add_text(c, heute, pos)
    [c,pos] = add_text(c, battery_number, pos)
    [c,pos] = add_text(c, weather, pos)
    [c,pos] = add_text(c, field, pos)
    [c,up_pos] = add_text(c, work_type, pos)
    return c, up_pos



if __name__ == "__main__":
    path = f"Documents/"
    title = input("Enter the title of your pdf file  ")
    weather = input("Enter the type of weather  ")
    c = create_pdf(path, title)
    title = "Gen.Farm RICA Field Test: Daily Report"
    subtitle = "Metadata"
    [c,pos] = add_title(c,title,570)
    [c,pos] = add_subtitle(c,subtitle,pos)
    [c,pos] = add_metadata(c,weather,pos)
    print(pos)
    c.showPage()
    c.save()
