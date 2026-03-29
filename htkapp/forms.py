from django import forms
from .models import Order, Product
import re

class CheckoutForm(forms.ModelForm):

    name = forms.CharField(max_length=100)
    pincode = forms.CharField(max_length=6)

    address_line1 = forms.CharField(max_length=100)
    address_line2 = forms.CharField(max_length=100)
    landmark = forms.CharField(max_length=100, required=False)

    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)

    class Meta:
        model = Order
        fields = ['phone']   # address will be built manually

    # ✅ NAME VALIDATION
    def clean_name(self):
        name = self.cleaned_data.get("name")

        if not re.match(r'^[A-Za-z]', name):
            raise forms.ValidationError("Name must start with an alphabet")

        if not re.match(r'^[A-Za-z ]+$', name):
            raise forms.ValidationError("Name must contain only letters")

        return name

    # ✅ PHONE VALIDATION
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not re.match(r'^[6-9]\d{9}$', phone):
            raise forms.ValidationError("Enter valid phone number")

        return phone

    # ✅ PINCODE VALIDATION
    def clean_pincode(self):
        pincode = self.cleaned_data.get("pincode")

        if not pincode.isdigit() or len(pincode) != 6:
            raise forms.ValidationError("Pincode must be 6 digits")

        return pincode

    # ✅ CITY / STATE VALIDATION
    def clean_city(self):
        city = self.cleaned_data.get("city")

        if not re.match(r'^[A-Za-z ]+$', city):
            raise forms.ValidationError("City must contain only letters")

        return city

    def clean_state(self):
        state = self.cleaned_data.get("state")

        if not re.match(r'^[A-Za-z ]+$', state):
            raise forms.ValidationError("State must contain only letters")

        return state
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # ✅ NAME
        self.fields['name'].widget.attrs.update({
            'id': 'name',
            'onkeyup': 'validateName()'
        })

        # ✅ PHONE
        self.fields['phone'].widget.attrs.update({
            'id': 'phone',
            'onkeyup': 'validatePhone()'
        })

        # ✅ ADDRESS
        self.fields['address_line1'].widget.attrs.update({
            'id': 'address1',
            'onkeyup': 'validateAddress1()'
        })

        self.fields['address_line2'].widget.attrs.update({
            'id': 'address2',
            'onkeyup': 'validateAddress2()'
        })

        # ✅ PINCODE (IMPORTANT 🔥)
        self.fields['pincode'].widget.attrs.update({
            'id': 'pincode',
            'onkeyup': 'validatePincode(); fetchLocation();'
        })

        # ✅ CITY (readonly + validation)
        self.fields['city'].widget.attrs.update({
            'id': 'city',
            'readonly': 'readonly',
        })

        # ✅ STATE
        self.fields['state'].widget.attrs.update({
            'id': 'state',
            'readonly': 'readonly',
        })
    def get_full_address(self):
            data = self.cleaned_data

            address = f"""
        {data.get('address_line1')}
        {data.get('address_line2')}
        {data.get('landmark', '')}
        {data.get('city')} - {data.get('pincode')}
        {data.get('state')}
        """

            return address.strip()
        

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()  # ✅ strong validation
    message = forms.CharField(widget=forms.Textarea)


# 🔥 PRODUCT FORM FOR ADMIN UPLOADS (validation + ImageField handling)
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock', 'description', 
                 'card_image', 'detail_image', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'card_image': forms.FileInput(attrs={'class': 'form-control'}),
            'detail_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_card_image(self):
        image = self.cleaned_data.get('card_image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB max
                raise forms.ValidationError("Card image too large (max 5MB)")
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Card image must be an image")
        return image
    
    def clean_detail_image(self):
        image = self.cleaned_data.get('detail_image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB max
                raise forms.ValidationError("Detail image too large (max 5MB)")
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Detail image must be an image")
        return image
