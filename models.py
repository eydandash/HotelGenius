from django.db import models

# All database models are created here.

# this is dirty hotel model to store any hotel that is uploaded in the csv file.
class DirtyHotel(models.Model):
    name = models.CharField(max_length=264)
    city = models.CharField(max_length=264)
    country = models.CharField(max_length=264)
    address = models.CharField(max_length=264)
    state = models.CharField(max_length=264)

    def __str__(self):
        return self.name

# this is a Lanyon Hotel model to store any hotel in the lanyon file, by running a script one time to populate it.
class LanyonHotel(models.Model):
    lanyonId = models.CharField(max_length=264, primary_key=True)
    name = models.CharField(max_length=264)
    city = models.CharField(max_length=264)
    country = models.CharField(max_length=264)
    address = models.CharField(max_length=264)
    state = models.CharField(max_length=264)

    def __str__(self):
        return self.name

# this table holds all hotel that have been cleaned during cleaning.
class CleanedHotel(models.Model):
    dirtyHotel = models.ForeignKey('DirtyHotel', on_delete=models.CASCADE)
    lanyonId = models.CharField(max_length=264, primary_key=True)
    name = models.CharField(max_length=264)
    city = models.CharField(max_length=264)
    country = models.CharField(max_length=264)
    address = models.CharField(max_length=264)
    state = models.CharField(max_length=264)

    def __str__(self):
        return self.name

# this table holds all hotels that could not be cleaned.
class UncleanedHotel(models.Model):
    dirtyHotel = models.ForeignKey('DirtyHotel', on_delete=models.CASCADE)

    def __str__(self):
        return self.dirtyHotel.name




