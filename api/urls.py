from django.urls import path, include
from .views import UploadAndProcess, ReceiveSelect, SubmitDescription, VoteDescription, VerifyCharacter, RequestDataSetBuild, TrainNetworks
urlpatterns = [
    #path('', Setup.as_view()),
    path('UploadHandler', UploadAndProcess.as_view()),
    path('Select', ReceiveSelect.as_view()),
    path('SubmitDescription', SubmitDescription.as_view()),
    path('VoteDescription', VoteDescription.as_view()),
    path('VerifyCharacter', VerifyCharacter.as_view()),
    path('BuildDataset', RequestDataSetBuild.as_view()),
    path('TrainNetworks', TrainNetworks.as_view())
]