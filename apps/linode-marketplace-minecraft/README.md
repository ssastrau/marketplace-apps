# Linode Minecraft Deployment One-Click APP

Minecraft is one of the most popular sandbox games and LinuxGSM is a lightweight tool that helps manage game servers from the command line. This Quick Deploy App provisions a Minecraft Java server with LinuxGSM so you can start managing the server immediately after deployment.

## Software Included

| Software | Version | Description |
| :--- | :---- | :--- |
| Minecraft Java Server | `latest` | Self-hosted Minecraft server |
| LinuxGSM | `latest` | Command line game server manager |

**Supported Distributions:**

- Ubuntu 24.04 LTS

## Deployment Details

Default service ports:
- SSH: `22/tcp`
- Minecraft: `25565/tcp`
- Minecraft: `25565/udp`

After deployment, credentials are written to:

- `/home/<sudo-user>/.credentials`

The credentials file includes:

- Sudo username/password
- LinuxGSM username/password
- Minecraft server port

Primary Minecraft config path:

- `/home/linuxgsm/serverfiles/server.properties`

## Managing Minecraft With LinuxGSM

If needed, switch to the LinuxGSM user first:

```bash
su - linuxgsm
cd /home/linuxgsm
```

Then run standard server commands:

```bash
./mcserver start
./mcserver stop
./mcserver restart
./mcserver console
```

If these values are not provided, deployment still completes and the default Linode DNS value is used.

## Resources

- [Minecraft Marketplace App Documentation](https://www.linode.com/marketplace/apps/linode/minecraft/)
- [LinuxGSM Documentation](https://docs.linuxgsm.com)
