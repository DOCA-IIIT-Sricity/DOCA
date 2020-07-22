from django.shortcuts import render
from django.http import HttpResponse
from accounts.decorators import isDoctor

@isDoctor(1)
def home(request):
    return HttpResponse("Welocome to Home")


def apply(request):
    specialization = [
    "Allergist",
    "Anaesthesiologist",
    "Andrologist",
    "Cardiologist",
    "Cardiac Electrophysiologist",
    "Dermatologist",
    "Emergency Room Doctors",
    "Endocrinologist",
    "Epidemiologist",
    "Family Medicine Physician",
    "Gastroenterologist",
    "Geriatrician",
    "Hyperbaric Physician",
    "Hematologist",
    "Hepatologist",
    "Immunologist",
    "Infectious Disease Specialist",
    "Intensivist",
    "Internal Medicine Specialist",
    "Maxillofacial Surgeon / Oral Surgeon",
    "Medical Examiner",
    "Medical Geneticist",
    "Neonatologist",
    "Nephrologist",
    "Neurologist",
    "Neurosurgeon",
    "Nuclear Medicine Specialist",
    "Gynecologist",
    "Occupational Medicine Specialist",
    "Oncologist",
    "Ophthalmologist",
    "Orthopedist",
    "Otolaryngologist",
    "Parasitologist",
    "Pathologist",
    "Perinatologist",
    "Periodontist",
    "Pediatrician",
    "Physiatrist",
    "Plastic Surgeon",
    "Psychiatrist",
    "Pulmonologist",
    "Radiologist",
    "Rheumatologist",
    "Sleep Disorders Specialist",
    "Spinal Cord Injury Specialist",
    "Sports Medicine Specialist",
    "Surgeon",
    "Thoracic Surgeon",
    "Urologist",
    "Vascular Surgeon",
    "Veterinarian",
    "Palliative Care Specialist",
    ]
    return render(request, 'accounts/applyasdoctor.html')
