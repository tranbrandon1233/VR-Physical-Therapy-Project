using System;
using TMPro;
using UnityEngine;
using UnityEngine.Android;
using UnityEngine.UI;

namespace OpenAI
{
    public class WhisperVoice : MonoBehaviour
    {
        public static event Action OnStartRecording;
        public static event Action<String> OnEndRecording;
        
        // [SerializeField] private Button recordButton;
        // [SerializeField] private Sprite micImage;
        // [SerializeField] private Sprite stopRec;
        // [SerializeField] private TMP_Dropdown dropdown;
        
        private readonly string fileName = "output.wav";
        private readonly int duration = 20;

        private bool isRecording;
        private AudioClip clip;
        private float time;
        private OpenAIApi openai = new OpenAIApi("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");

        private void Start()
        {
            if (!Permission.HasUserAuthorizedPermission(Permission.Microphone))
            {
                Permission.RequestUserPermission(Permission.Microphone);
            }
            
            #if UNITY_WEBGL && !UNITY_EDITOR
            dropdown.options.Add(new Dropdown.OptionData("Microphone not supported on WebGL"));
            #else
            // foreach (var device in Microphone.devices)
            // {
            //     dropdown.options.Add(new TMP_Dropdown.OptionData(device));
            // }
            // recordButton.onClick.AddListener(StartRecording);
            // dropdown.onValueChanged.AddListener(ChangeMicrophone);
            
            // var index = PlayerPrefs.GetInt("user-mic-device-index");
            // dropdown.SetValueWithoutNotify(index);
            #endif
        }

        private void OnEnable()
        {
            OnStartRecording += UpdateRecordButton;
            OnEndRecording += UpdateRecordButton;
        }
        
        private void OnDisable()
        {
            OnStartRecording -= UpdateRecordButton;
            OnEndRecording -= UpdateRecordButton;
        }

        private void Update()
        {
            if (isRecording)
            {
                if (OVRInput.GetDown(OVRInput.Button.One, OVRInput.Controller.RTouch)) 
                {
                    EndRecording();
                }
            }
            else
            {
                if (OVRInput.GetDown(OVRInput.Button.One, OVRInput.Controller.RTouch)) 
                {
                    StartRecording();
                }
            }
        }

        private void UpdateRecordButton()
        {
            // if (isRecording)
            // {
            //     recordButton.image.sprite = stopRec;
            //     recordButton.onClick.RemoveListener(StartRecording);
            //     recordButton.onClick.AddListener(EndRecording);
            // }
            // else
            // {
            //     recordButton.image.sprite = micImage;
            //     recordButton.onClick.RemoveListener(EndRecording);
            //     recordButton.onClick.AddListener(StartRecording);
            // }
        }
        private void UpdateRecordButton(string text)
        {
            // if (isRecording)
            // {
            //     recordButton.onClick.RemoveListener(StartRecording);
            //     recordButton.onClick.AddListener(EndRecording);
            // }
            // else
            // {
            //     recordButton.image.sprite = micImage;
            //     recordButton.onClick.RemoveListener(EndRecording);
            //     recordButton.onClick.AddListener(StartRecording);
            // }
        }

        // private void ChangeMicrophone(int index)
        // {
        //     PlayerPrefs.SetInt("user-mic-device-index", index);
        // }
        
        private void StartRecording()
        {
            isRecording = true;
            OnStartRecording?.Invoke();
            // recordButton.enabled = false;

            var index = PlayerPrefs.GetInt("user-mic-device-index");
            
            #if !UNITY_WEBGL
            // clip = Microphone.Start(dropdown.options[index].text, false, duration, 44100);
            clip = Microphone.Start(Microphone.devices[0], true, duration, AudioSettings.outputSampleRate);
            // print("Microphone.devices[0]: " + Microphone.devices[0]);
            // print("List of Microphone.devices: " + string.Join(", ", Microphone.devices));
            #endif
        }

        // TODO: Automatically End Recording when user stops talking: https://stackoverflow.com/questions/40913081/unity-microphone-check-if-silent
        private async void EndRecording()
        {
            // recordButton.interactable = false;
            // recordButton.GetComponentInChildren<TMP_Text>().text = "Transcribing...";
            
            #if !UNITY_WEBGL
            Microphone.End(null);
            #endif
            
            byte[] data = SaveWav.Save(fileName, clip);
            
            var req = new CreateAudioTranscriptionsRequest
            {
                FileData = new FileData() {Data = data, Name = "audio.wav"},
                // File = Application.persistentDataPath + "/" + fileName,
                Model = "whisper-1",
                Language = "en"
            };
            var res = await openai.CreateAudioTranscription(req);
            
            isRecording = false;
            print("You said this: " + res.Text);
            OnEndRecording?.Invoke(res.Text);  // Maybe edge case of it still doing async function when this is called and another function expects the end to be done.
        }
    }
}
