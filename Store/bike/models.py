# Store>bike>models.py
from django.db import models
from django.shortcuts import render
from django.http import JsonResponse
import openai

openai.api_key = 'your-openai-api-key'

def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        
        # Call the ChatGPT model to generate a response
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=user_input,
            max_tokens=50
        )
        
        return JsonResponse({'response': response['choices'][0]['text'].strip()})
    else:
        return render(request, 'chat.html')


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    featured = models.BooleanField(default=False)  # New field for featured products
    quantity = models.IntegerField(default=250)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    quantity = models.IntegerField(default=1)
    date_ordered = models.DateTimeField(auto_now_add=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    delivery_status = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"