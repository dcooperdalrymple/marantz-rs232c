#include "esphome.h"

class UartVolumeSensor : public PollingComponent, public UARTDevice, public Sensor {
    public:
        UartVolumeSensor(UARTComponent *parent, int id) : PollingComponent(10000), UARTDevice(parent), device_id(id) {}

        void setup() override { }

        int readline(int readch, char *buffer, int len) {
            static int pos = 0;
            int rpos;

            if (readch > 0) {
                switch (readch) {
                    case '\n': // Ignore new-lines
                        break;
                    case 0x0D: // Return on CR
                        rpos = pos;
                        pos = 0;  // Reset position index ready for next time
                        return rpos;
                    default:
                        if (pos < len-1) {
                            buffer[pos++] = readch;
                            buffer[pos] = 0;
                        }
                }
            }
            // No end of line has been found, so return -1.
            return -1;
        }

        float readvalue(char *buffer, int len) {
            int rpos = 0;
            memset(buffer, 0, len); // Clear buffer
            while (available()) {
                rpos = readline(read(), buffer, len);
                if (rpos > 0) break;
            }
            if (rpos < 6) return -100.0;

            // Validate response
            if (buffer[0] != 0x40) return -100.0; // '@'
            if (buffer[1] != device_id) return -100.0;
            if (buffer[2] != 0x48) return -100.0; // 'H'

            // Check volume state
            if (buffer[3] == 0x30) { // '0'
                // Extract number from response
                for (int i = 0; i < 3; i++) {
                    buffer[i] = buffer[i+4];
                }
                buffer[3] = '\0';
                return atof(buffer);
            } else if (buffer[3] == 0x31) { // '1'
                // Max
                return 99.0;
            } else if (buffer[3] == 0x32) { // '2'
                // Min
                return -90.0;
            }

            return -100.0;
        }

        void update() override {
            const int max_len = 8; // 5 for request, 8 for return

            // Request Status
            static char buffer[max_len] = {0x40, device_id, 0x3F, 0x48, 0x0D, 0x00, 0x00, 0x00}; // @1 ?H \n
            write(buffer, 5);
            delay(100);

            // Read Response (if available)
            float value = readvalue(buffer, max_len);
            if (value != -100.0) publish_state(value);
        }

    private:
        int device_id;

};
