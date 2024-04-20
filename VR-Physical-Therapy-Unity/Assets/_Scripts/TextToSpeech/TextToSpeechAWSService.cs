using System.IO;
using System.Threading.Tasks;
using Amazon;
using Amazon.Polly;
using Amazon.Polly.Model;
using Amazon.Runtime;

namespace AWS
{
    public class TextToSpeechAWSService
    {
        private AmazonPollyClient _client;
        
        public TextToSpeechAWSService(string accessKey, string secretKey, RegionEndpoint regionEndpoint = null)
        {
            var credentials = new BasicAWSCredentials(accessKey, secretKey);
            var config = new AmazonPollyConfig
            {
                RegionEndpoint = regionEndpoint ?? RegionEndpoint.USWest2
            };

            _client = new AmazonPollyClient(credentials, config);
        }

        public async Task ConvertTextToSpeechAsync(string text, string outputPath, VoiceId voiceId)
        {
            var request = new SynthesizeSpeechRequest
            {
                Text = text,
                Engine = Engine.Neural,
                VoiceId = voiceId,
                OutputFormat = OutputFormat.Mp3,
            };

            var response = await _client.SynthesizeSpeechAsync(request);
            WriteIntoFile(response.AudioStream, outputPath);
        }

        private void WriteIntoFile(Stream stream, string outputPath)
        {
            using (var fileStream = new FileStream(outputPath, FileMode.Create))
            {
                byte[] buffer = new byte[8 * 1024];
                int bytesRead;
                while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
                {
                    fileStream.Write(buffer, 0, bytesRead);
                }
            }
        }
    }
}

