from PIL import Image, ImageDraw

def create_icon():
    # Create a 256x256 image with a transparent background
    icon = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw a dark background circle
    draw.ellipse((10, 10, 246, 246), fill=(33, 33, 33, 255))
    
    # Draw a microphone shape
    draw.rectangle((108, 70, 148, 170), fill=(200, 50, 50, 255), outline=(220, 70, 70, 255), width=2)
    draw.ellipse((98, 60, 158, 90), fill=(200, 50, 50, 255), outline=(220, 70, 70, 255), width=2)
    
    # Draw a stand
    draw.rectangle((118, 170, 138, 190), fill=(180, 180, 180, 255))
    draw.ellipse((108, 190, 148, 210), fill=(150, 150, 150, 255))
    
    # Draw YouTube-like play button
    draw.polygon([(170, 110), (170, 150), (200, 130)], fill=(255, 255, 255, 255))
    
    # Save as PNG first
    icon.save('icon.png')
    
    # Save as ICO for Windows
    icon.save('icon.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    
    print("Icon created successfully!")

if __name__ == "__main__":
    create_icon()
