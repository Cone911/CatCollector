from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import requests
from .models import Cat, Toy
from .forms import FeedingForm

# Create your views here.
class Home(LoginView):
  template_name = 'home.html'

def about(request):
  response = requests.get('https://catfact.ninja/fact')
  return render(request, 'about.html', {
    'fact': response.json().get('fact')
  })

@login_required
def cat_index(request):
    cats = Cat.objects.filter(user=request.user)
    # You could also retrieve the logged in user's cats like this
    # cats = request.user.cat_set.all()
    return render(request, 'cats/index.html', { 'cats': cats })

def cat_detail(request, cat_id):
  cat = Cat.objects.get(id=cat_id)
  # toys = Toy.objects.all()  # Fetch all toys
  toy_ids_cat_has = cat.toys.all().values_list('id')
  toys_cat_doesnt_have = Toy.objects.exclude(id__in=toy_ids_cat_has)
  feeding_form = FeedingForm()
  return render(request, 'cats/detail.html', {
    'cat': cat,
    'feeding_form': feeding_form,
    'toys': toys_cat_doesnt_have,
  })

class CatCreate(CreateView, LoginRequiredMixin):
  model = Cat
  fields = ['name', 'breed', 'description', 'age']
  # success_url = '/cats/{id}'

  def form_valid(self, form):
    #Assign the logged-in user to the new cat object's user_id attribute.
    form.instance.user = self.request.user
    # Let the inherited form_valid method handle the saving of the form data.
    return super().form_valid(form)

class CatUpdate(UpdateView, LoginRequiredMixin):
  model = Cat
  fields = ['breed', 'description', 'age']

class CatDelete(DeleteView, LoginRequiredMixin):
  model = Cat
  success_url = '/cats/'

@login_required
def add_feeding(request, cat_id):
  # request.POST is a QueryDict (dictionary-like object)
  form = FeedingForm(request.POST)
  if form.is_valid():
    # Create a feeding object, but don't save it yet to the database (in memory only)
    new_feeding = form.save(commit=False)
    new_feeding.cat_id = cat_id
    new_feeding.save()
  return redirect('cat-detail', cat_id=cat_id)

class ToyCreate(CreateView, LoginRequiredMixin):
  model = Toy
  fields = '__all__'

class ToyList(ListView, LoginRequiredMixin):
  model = Toy

class ToyDetail(DetailView, LoginRequiredMixin):
  model = Toy

class ToyUpdate(UpdateView, LoginRequiredMixin):
  model = Toy
  fields = ['name', 'color']

class ToyDelete(DeleteView, LoginRequiredMixin):
  model = Toy
  success_url = '/toys/'

@login_required
def associate_toy(request, cat_id, toy_id):
    # Note that you can pass a toy's id instead of the whole object
    
    # cat = Cat.objects.get(id=cat_id)
    # cat.toys.add(toy_id)
    # or in one line:

    Cat.objects.get(id=cat_id).toys.add(toy_id)
    return redirect('cat-detail', cat_id=cat_id)

# Create the view function. Hint: use Django's .remove() method
@login_required
def remove_toy(request, cat_id, toy_id):
  #Look up the cat
  cat = Cat.objects.get(id=cat_id)
  #Look up the toy
  toy = Toy.objects.get(id=toy_id)
  #Remove the toy from the cat's toys
  cat.toys.remove(toy)
  return redirect('cat-detail', cat_id=cat_id)

def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in
            login(request, user)
            return redirect('cat-index')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)
    # Same as: 
    # return render(
    #     request, 
    #     'signup.html',
    #     {'form': form, 'error_message': error_message}
    # )


